# Implement Deep Learning based Rppg Model using pytorch

### model list

- #### Facial Image Based ppg measurement algorithm
- [x] [DeepPhys : DeepPhys: Video-Based Physiological Measurement Using Convolutional Attention Networks](https://arxiv.org/abs/1805.07888)
- [ ] [MTTS  :Multi-Task Temporal Shift Attention Networks for
On-Device Contactless Vitals Measurement](https://papers.nips.cc/paper/2020/file/e1228be46de6a0234ac22ded31417bc7-Paper.pdf)
  + need to verification
- [x] DeepPhys + LSTM
- [x] [3D physNet :  Remote Photoplethysmograph Signal Measurement from Facial Videos Using Spatio-Temporal Networks](https://arxiv.org/abs/1905.02419)
- [x] [2D phsyNet + LSTM](https://arxiv.org/abs/1905.02419)

- #### PPG Based Blood Pressure estimation algorithm
- [x] [PP-Net: A Deep Learning Framework for PPG based Blood Pressure and Heart Rate Estimation](https://ieeexplore.ieee.org/document/9082808)

## file list

- dataset&nbsp; :&nbsp; related to dataset
  + dataset_loader.py&nbsp; :&nbsp; pytorch.utils.dataset stored dataset file load(.hpy)
  + __NetworkName__Dataset.py&nbsp; :&nbsp; Customized dataset to fit each model.
  

- nets&nbsp; :&nbsp; related to Network Architecture
  <br/>(&nbsp;funcs&nbsp;<&nbsp;layers&nbsp;<&nbsp;blocks&nbsp;<&nbsp;modules&nbsp;<=&nbsp;sub_models&nbsp;<=&nbsp;models)
  + blocks
  + funcs
  + layers
  + models
    + sub_models
  + modules
  

- log.py&nbsp; :&nbsp; custom log functions
- loss.py &nbsp;:&nbsp; available loss list & custom loss functions
- optim.py &nbsp;:&nbsp; available optimizer list & custom optimizer functions
- main.py
- params.json &nbsp;:&nbsp;List of options for training


### preprocessor list
- \_\_TIME__ &nbsp;:&nbsp; check features running time
  + preprocessing time
  + model init time
  + setting loss func time
  + setting optimizer time
  + training time per 1epoch
  + inference time per 1 batch 
  

- \_\_PREPROCESSING__&nbsp; :&nbsp; perform preprocessing before training & generate preprocessed file(.hpy)

- \_\_MODEL_SUMMARY__&nbsp; :&nbsp; print model architecture summary using torchsummary

## Usages
1. modify params.json
~~~
example
  "model_params":
    {
        "name": "DeepPhys",
        "name_comment":
                [
                    "DeepPhys",
                    "PhysNet"
                ]
    }
~~~ 
2. run main.py

## Contacts
TVSTORM inc.\
Kim Dae Yeol &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Kim Jin Soo\
wagon0004@tvstorm.com &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;wlstn25092303@tvstorm.com


Kwangkee Lee, kwangkeelee@gmail.com

## Funding
 This work was supported by the ICT R&D program of MSIP/IITP. [2021(2021-0-00900), Adaptive Federated Learning in Dynamic Heterogeneous Environment]

## reference
1. [ZitongYu/PhysNet](https://github.com/ZitongYu/PhysNet)
