import torch
from torch import nn
from pytorch3d.ops import knn_points
from utils.cloth_and_material import FaceNormals
from utils.common import gather

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    weight_start: float = 1e+3
    weight_max: float = 1e+5
    start_rampup_iteration: int = 50000
    n_rampup_iterations: int = 100000
    eps: float = 1e-3


def create(mcfg):
    return Criterion(weight_start=mcfg.weight_start, weight_max=mcfg.weight_max,
                     start_rampup_iteration=mcfg.start_rampup_iteration, n_rampup_iterations=mcfg.n_rampup_iterations,
                     eps=mcfg.eps)



class Criterion(nn.Module):
    def __init__(self, weight_start, weight_max, start_rampup_iteration, n_rampup_iterations, eps=1e-3):
        super().__init__()
        self.weight_start = weight_start
        self.weight_max = weight_max
        self.start_rampup_iteration = start_rampup_iteration
        self.n_rampup_iterations = n_rampup_iterations
        self.eps = eps
        self.f_normals_f = FaceNormals()
        self.name = 'collision_penalty'

    def get_weight(self, iter):
        iter = iter - self.start_rampup_iteration
        iter = max(iter, 0)
        progress = iter / self.n_rampup_iterations
        progress = min(progress, 1.)
        weight = self.weight_start + (self.weight_max - self.weight_start) * progress
        return weight

    def calc_loss(self, example):
        obstacle_next_pos = example['obstacle'].target_pos
        obstacle_curr_pos = example['obstacle'].pos
        obstacle_faces = example['obstacle'].faces_batch.T

        curr_pos = example['cloth'].pos
        next_pos = example['cloth'].pred_pos

        # Find correspondences in current step
        obstacle_face_curr_pos = gather(obstacle_curr_pos, obstacle_faces, 0, 1, 1).mean(dim=-2)
        _, nn_idx, _ = knn_points(curr_pos.unsqueeze(0), obstacle_face_curr_pos.unsqueeze(0),
                                  return_nn=True)
        nn_idx = nn_idx[0]

        # Compute distances in the new step
        obstacle_face_next_pos = gather(obstacle_next_pos, obstacle_faces, 0, 1, 1).mean(dim=-2)
        obstacle_fn = self.f_normals_f(obstacle_next_pos.unsqueeze(0), obstacle_faces.unsqueeze(0))[0]

        nn_points = gather(obstacle_face_next_pos, nn_idx, 0, 1, 1)
        nn_normals = gather(obstacle_fn, nn_idx, 0, 1, 1)

        nn_points = nn_points[:, 0]
        nn_normals = nn_normals[:, 0]
        device = next_pos.device

        distance = ((next_pos - nn_points) * nn_normals).sum(dim=-1)
        interpenetration = torch.maximum(self.eps - distance, torch.FloatTensor([0]).to(device))

        interpenetration = interpenetration.pow(3)
        loss = interpenetration.sum(-1)

        return loss

    def forward(self, sample):
        B = sample.num_graphs
        iter_num = sample['cloth'].iter[0].item()
        weight = self.get_weight(iter_num)

        loss_list = []
        for i in range(B):
            loss_list.append(
                self.calc_loss(sample.get_example(i)))

        loss = sum(loss_list) / B * weight

        return dict(loss=loss)
# class Criterion(nn.Module):
#     def __init__(self, weight_start, weight_max, start_rampup_iteration, n_rampup_iterations, eps=1e-3):
#         super().__init__()
#         self.weight_start = weight_start
#         self.weight_max = weight_max
#         self.start_rampup_iteration = start_rampup_iteration
#         self.n_rampup_iterations = n_rampup_iterations
#         self.eps = eps
#         self.f_normals_f = FaceNormals()
#         self.name = 'collision_penalty'

#     def get_weight(self, iter):
#         iter = iter - self.start_rampup_iteration
#         iter = max(iter, 0)
#         progress = iter / self.n_rampup_iterations
#         progress = min(progress, 1.)
#         weight = self.weight_start + (self.weight_max - self.weight_start) * progress
#         return weight

#     def calc_external_penetration_loss(self, cloth_pos, obstacle_pos, obstacle_faces, obstacle_normals):
#         # 计算布料与障碍物之间的穿透损失 L𝑒
#         _, nn_idx, _ = knn_points(cloth_pos.unsqueeze(0), obstacle_pos.unsqueeze(0), return_nn=True)
#         nn_idx = nn_idx[0]
#         nn_normals = gather(obstacle_normals, nn_idx, 0, 1, 1)[:, 0]
        
#         distances = ((cloth_pos - obstacle_pos[nn_idx]) * nn_normals).sum(dim=-1)
#         external_penetration = torch.maximum(self.eps - distances, torch.zeros_like(distances))
#         external_penetration_loss = external_penetration.pow(3).sum(-1)
        
#         return external_penetration_loss

#     def calc_self_penetration_loss(self, cloth_pos, cloth_normals):
#         # 计算布料自身的穿透损失 L𝑠
#         _, nn_idx, _ = knn_points(cloth_pos.unsqueeze(0), cloth_pos.unsqueeze(0), return_nn=True)
#         nn_idx = nn_idx[0]
        
#         nn_normals = gather(cloth_normals, nn_idx, 0, 1, 1)[:, 0]
        
#         distances = ((cloth_pos - cloth_pos[nn_idx]) * nn_normals).sum(dim=-1)
#         self_penetration = torch.maximum(self.eps - distances, torch.zeros_like(distances))
#         self_penetration_loss = self_penetration.pow(3).sum(-1)
        
#         return self_penetration_loss
    
#     def calc_loss(self, example):
#         obstacle_next_pos = example['obstacle'].target_pos
#         obstacle_curr_pos = example['obstacle'].pos
#         obstacle_faces = example['obstacle'].faces_batch.T

#         curr_pos = example['cloth'].pos
#         next_pos = example['cloth'].pred_pos

#         # Find correspondences in current step
#         obstacle_face_curr_pos = gather(obstacle_curr_pos, obstacle_faces, 0, 1, 1).mean(dim=-2)
#         _, nn_idx, _ = knn_points(curr_pos.unsqueeze(0), obstacle_face_curr_pos.unsqueeze(0),
#                                   return_nn=True)
#         nn_idx = nn_idx[0]

#         # Compute distances in the new step
#         obstacle_face_next_pos = gather(obstacle_next_pos, obstacle_faces, 0, 1, 1).mean(dim=-2)
#         obstacle_fn = self.f_normals_f(obstacle_next_pos.unsqueeze(0), obstacle_faces.unsqueeze(0))[0]

#         nn_points = gather(obstacle_face_next_pos, nn_idx, 0, 1, 1)
#         nn_normals = gather(obstacle_fn, nn_idx, 0, 1, 1)

#         nn_points = nn_points[:, 0]
#         nn_normals = nn_normals[:, 0]
#         device = next_pos.device

#         distance = ((next_pos - nn_points) * nn_normals).sum(dim=-1)

#         # Assuming cloth_normals is already computed and provided
#         cloth_normals = example['cloth'].normals  # You need to provide the cloth normals
#         #print(cloth_normals)
        
#         # Calculate external and self penetration losses
#         external_loss = self.calc_external_penetration_loss(next_pos, obstacle_face_next_pos, obstacle_faces, obstacle_fn)
#         self_loss = self.calc_self_penetration_loss(next_pos, cloth_normals)

#         # Total loss
#         loss = external_loss + self_loss

#         # Convert loss to a scalar if it's not already
#         loss_dict = {'loss': loss}
#         if not loss_dict['loss'].numel() == 1:  # Check if the loss is a scalar
#             loss_dict['loss'] = loss_dict['loss'].sum()  # Or loss_dict['loss'].mean() if you want the average

#         return loss_dict

#     def forward(self, sample):
#         B = sample.num_graphs
#         iter_num = sample['cloth'].iter[0].item()
#         weight = self.get_weight(iter_num)

#         loss_list = []
#         for i in range(B):
#             loss_dict = self.calc_loss(sample.get_example(i))
#             # Ensure the loss is a scalar before appending
#             loss_list.append(loss_dict['loss'].sum())  # Or loss_dict['loss'].mean() if you want the average

#         total_loss = sum(loss_list) / B * weight

#         return dict(loss=total_loss)
