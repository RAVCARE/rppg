import torchinfo
import torchsummary

from log import log_warning, log_info
from nets.models.AxisNet import AxisNet,PhysiologicalGenerator
from nets.models.DeepPhys import DeepPhys
from nets.models.DeepPhys_DA import DeepPhys_DA
from nets.models.PPNet import PPNet
from nets.models.PhysNet import PhysNet
from nets.models.PhysNet import PhysNet_2DCNN_LSTM
from nets.models.Seq_GCN import Seq_GCN
from nets.models.TEST import TEST,TEST2
from nets.models.RhythmNet import RhythmNet
from nets.models.ETArPPGNet import ETArPPGNet
from nets.models.sub_models.Vitamon import Vitamon

import os
NUM_FEATURES = 5
NUM_CLASSES = 10

def get_ver_model(model_name: str = "DeepPhys", ver:int = 1):
    return TEST2(ver)


def get_model(model_name: str = 'DeepPhys', log_flag:bool = True):
    """
    :param model_name: model name
    :return: model
    """
    if log_flag:
        print("========= set model get_model() in"+ os.path.basename(__file__))

    if model_name == "DeepPhys":
        return DeepPhys()
    elif model_name == "DeepPhys_DA":
        return DeepPhys_DA()
    elif model_name == "PhysNet":
        return PhysNet()
    elif model_name == "PhysNet_LSTM":
        return PhysNet_2DCNN_LSTM()
    elif model_name == "PPNet":
        return PPNet()
    elif model_name == "GCN":
        return TEST()#Seq_GCN()#TEST()#
    elif model_name == "AxisNet":
        return AxisNet(),PhysiologicalGenerator()
    elif model_name == "RhythmNet":
        return RhythmNet()
    elif model_name == "ETArPPGNet":
        return ETArPPGNet()
    elif model_name == "Vitamon":
        return Vitamon()
    else:
        log_warning("use implemented model")
        raise NotImplementedError("implement a custom model(%s) in /nets/models/" % model_name)


def is_model_support(model_name, model_list, log_flag):
    """
    :param model_name: model name
    :param model_list: implemented model list
    :return: model
    """
    if log_flag:
        print("========= model support check is model support() in " + os.path.basename(__file__))
    if not (model_name in model_list):
        log_warning("use implemented model")
        raise NotImplementedError("implement a custom model(%s) in /nets/models/" % model_name)


def summary(model, model_name):
    """
    :param model: torch.nn.module class
    :param model_name: implemented model name
    :return: model
    """
    log_info("=========================================")
    log_info(model_name)
    log_info("=========================================")
    if model_name == "DeepPhys" or model_name == DeepPhys_DA:
        torchsummary.summary(model, (2, 3, 36, 36))
    elif model_name == "PhysNet" or model_name == "PhysNet_LSTM":
        torchinfo.summary(model, (1, 3, 32, 128, 128))
    elif model_name in "PPNet":
        torchinfo.summary(model, (1, 1, 250))
    elif model_name in "GCN":
        log_warning("some module is not supported in torchinfo")
        torchinfo.summary(model,(32,3,32,32,32))
    else:
        log_warning("use implemented model")
        raise NotImplementedError("implement a custom model(%s) in /nets/models/" % model_name)
