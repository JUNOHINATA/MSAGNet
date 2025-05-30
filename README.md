garment simulation
### Install conda enviroment
We provide a conda environment file `hood.yml` to install all the dependencies. 
You can create and activate the environment with the following commands:

```bash
conda env create -f hood.yml
conda activate hood
```

If you want to build the environment from scratch, here are the necessary commands: 
<details>
  <summary>Build enviroment from scratch</summary>

```bash
# Create and activate a new environment
conda create -n hood python=3.9 -y
conda activate hood

# install pytorch (see https://pytorch.org/)
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia -y

# install pytorch_geometric (see https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html)
conda install pyg -c pyg -y

# install pytorch3d (see https://github.com/facebookresearch/pytorch3d/blob/main/INSTALL.md)
conda install -c fvcore -c iopath -c conda-forge fvcore iopath -y
conda install -c bottler nvidiacub -y
conda install pytorch3d -c pytorch3d -y


# install auxiliary packages with conda
conda install -c conda-forge munch pandas tqdm omegaconf matplotlib einops ffmpeg -y

# install more auxiliary packages with pip
pip install smplx aitviewer chumpy huepy

# create a new kernel for jupyter notebook
conda install ipykernel -y; python -m ipykernel install --user --name hood --display-name "hood"
```
</details>

### Download data
#### HOOD data
Download the auxiliary data for HOOD using this [link](https://drive.google.com/file/d/1RdA4L6Fy50VsKZ8k7ySp5ps5YtWoHSgs/view?usp=sharing).
Unpack it anywhere you want and set the `HOOD_DATA` environmental variable to the path of the unpacked folder.
Also, set the `HOOD_PROJECT` environmental variable to the path you cloned this repository to(在inference.ipynb中设置好自己对应的路径):

```bash
export HOOD_DATA=/path/to/hood_data
export HOOD_PROJECT=/path/to/this/repository
```

#### SMPL models
Download the SMPL models using this [link](https://smpl.is.tue.mpg.de/). Unpack them into the `$HOOD_DATA/aux_data/smpl` folder.

In the end your `$HOOD_DATA` folder should look like this(严格按照要求完成文件夹):
```
$HOOD_DATA
    |-- aux_data
        |-- datasplits // directory with csv data splits used for training the model
        |-- smpl // directory with smpl models
            |-- SMPL_NEUTRAL.pkl
            |-- SMPL_FEMALE.pkl
            |-- SMPL_MALE.pkl
        |-- garment_meshes // folder with .obj meshes for garments used in HOOD
        |-- garments_dict.pkl // dictionary with garmentmeshes and their auxilliary data used for training and inference
        |-- smpl_aux.pkl // dictionary with indices of SMPL vertices that correspond to hands, used to disable hands during inference to avoid body self-intersections
    |-- trained_models // directory with trained HOOD models
        |-- cvpr_submission.pth // model used in the CVPR paper
        |-- postcvpr.pth // model trained with refactored code with several bug fixes after the CVPR submission
        |-- fine15.pth // baseline model without denoted as "Fine15" in the paper (15 message-passing steps, no long-range edges)
        |-- fine48.pth // baseline model without denoted as "Fine48" in the paper (48 message-passing steps, no long-range edges)
```

## Inference
The jupyter notebook [Inference.ipynb](Inference.ipynb) contains an example of how to run inference of a trained HOOD model given a garment and a pose sequence.

It also has examples of such use-cases as adding a new garment from an .obj file and converting sequences from [AMASS](https://amass.is.tue.mpg.de/) and [VTO](https://github.com/isantesteban/vto-dataset) datasets to the format used in HOOD.

To run inference starting from arbitrary garment pose and arbitrary mesh sequence refer to the [InferenceFromMeshSequence.ipynb](InferenceFromMeshSequence.ipynb) notebook.  

## Training
To train a new HOOD model from scratch, you need to first download the [VTO](https://github.com/isantesteban/vto-dataset) dataset and convert it to our format.

You can find the instructions on how to do that and the commands used to start the training in the [Training.ipynb](Training.ipynb) notebook.

## Validation Sequences
You can download the sequences used for validation (Table 1 in the main paper and Tables 1 and 2 in the Supplementary) 
using [this link](https://drive.google.com/file/d/1jFkDWPZW2HwYsYqcXAC3hX0NlumBnqT3/view?usp=sharing)

You can find instructions on how to generate validation sequences and compute metrics over them in the [ValidationSequences.ipynb](ValidationSequences.ipynb) notebook.

## 效果展示图
![image](https://github.com/JUNOHINATA/MSAGNet/blob/main/sample2.png)
![image](https://github.com/JUNOHINATA/MSAGNet/blob/main/sample3.png)
![image](https://github.com/JUNOHINATA/MSAGNet/blob/main/sample4.png)
![image](https://github.com/JUNOHINATA/MSAGNet/blob/main/sample5.png)

## 说明
根据inference.ipynb中的指示推理模型(请注意最好使用命令行进行渲染而不要使用改文件中的代码进行渲染).

如要自行生成结果请将生成的pkl文件分解为服装模型和人体模型,再使用如blender等工具进行自定义渲染.

根目录下的collision_penalty.py是修改后碰撞损失函数.

评价指标.ipynb用于计算每顶点平均误差等指标.

因有人构建hood_data文件夹失败,特放置hood_data文件夹如下:
链接: https://pan.baidu.com/s/1LjnHN6qXkH4xix1u-KJ4eg 提取码: 1234

