# ERNIEM Python部署指南
本文介绍 ERNIE 3.0 Python 端的部署，包括部署环境的准备，序列标注和分类两大场景下的使用示例。
- [ERNIE-M Python 部署指南](#ERNIEM-Python部署指南)
  - [1. 环境准备](#1-环境准备)
    - [1.1 CPU 端](#11-CPU端)
    - [1.2 GPU 端](#12-GPU端)
  - [2. 分类模型推理](#2-分类模型推理)
    - [2.1 模型获取](#21-模型获取)
    - [2.2 CPU 端推理样例](#22-CPU端推理样例)
    - [2.3 GPU 端推理样例](#23-GPU端推理样例)
## 1. 环境准备
ERNIE-M 的部署分为 CPU 和 GPU 两种情况，请根据你的部署环境安装对应的依赖。
### 1.1 CPU端
CPU 端的部署请使用如下命令安装所需依赖
```
pip install -r requirements_cpu.txt
```
### 1.2 GPU端
为了在 GPU 上获得最佳的推理性能和稳定性，请先确保机器已正确安装 NVIDIA 相关驱动和基础软件，确保 CUDA >= 11.2，CuDNN >= 8.2，并使用以下命令安装所需依赖
```
pip install -r requirements_gpu.txt
```


## 2. 模型推理
### 2.1 模型获取
用户可使用自己训练的模型进行推理，具体训练调优方法可参考[模型训练调优](./../../README.md#模型训练)

### 2.2 CPU端推理样例
在 CPU 端，请使用如下命令进行部署
```
python infer_cpu.py --task_name seq_cls --model_path ../../finetuned_models/export/model
```
输出打印如下:
```
input data: ['对成人和儿童来说很有趣。', '只有孩子才会开心。']
seq cls result:
label: entailment   confidence: 0.8088128566741943
-----------------------------
input data: ['下一个证人是玛丽·卡文迪什。', '还有另外一个证人。']
seq cls result:
label: entailment   confidence: 0.9145026206970215
-----------------------------
input data: ['过去20年的研究改变了生命的科学观点。', '过去5年的研究有更大的影响力。']
seq cls result:
label: entailment   confidence: 0.9125779271125793
-----------------------------
```
infer_cpu.py 脚本中的参数说明：
| 参数 |参数说明 |
|----------|--------------|
|--task_name | 配置任务名称，默认 seq_cls|
|--model_name_or_path | 模型的路径或者名字，默认为 ernie-m|
|--model_path | 用于推理的 Paddle 模型的路径|
|--max_seq_length |最大序列长度，默认为 256|
|--precision_mode | 推理精度，可选 fp32，fp16 或者 int8，当输入非量化模型并设置 int8 时使用动态量化进行加速，默认 fp32 |
|--num_threads | 配置 cpu 的线程数，默认为 cpu 的最大线程数 |

### 2.3 GPU端推理样例
在 GPU 端，请使用如下命令进行部署
```
python infer_gpu.py --task_name seq_cls --model_path ../../finetuned_models/export/model
```
输出打印如下:
```
input data: ['对成人和儿童来说很有趣。', '只有孩子才会开心。']
seq cls result:
label: entailment   confidence: 0.9821083545684814
-----------------------------
input data: ['下一个证人是玛丽·卡文迪什。', '还有另外一个证人。']
seq cls result:
label: entailment   confidence: 0.9955698847770691
-----------------------------
input data: ['过去20年的研究改变了生命的科学观点。', '过去5年的研究有更大的影响力。']
seq cls result:
label: entailment   confidence: 0.8629468679428101
-----------------------------
{'label': array([0, 0, 0]), 'confidence': array([0.98210835, 0.9955699 , 0.86294687], dtype=float32)}
```
如果需要 FP16 进行加速，可以设置 precision_mode 为 fp16，具体命令为
```
python infer_gpu.py --task_name seq_cls --model_path ../../finetuned_models/export/model --precision_mode fp16
```
infer_gpu.py 脚本中的参数说明：
| 参数 |参数说明 |
|----------|--------------|
|--task_name | 配置任务名称，可选 seq_cls|
|--model_name_or_path | 模型的路径或者名字，默认为ernie-m-base|
|--model_path | 用于推理的 Paddle 模型的路径|
|--batch_size |最大可测的 batch size，默认为 32|
|--max_seq_length |最大序列长度，默认为 256|
|--precision_mode | 推理精度，可选 fp32，fp16 或者 int8，默认 fp32 |