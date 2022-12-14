import os
import sys
import torch
import torch.backends.cudnn as cudnn
from torch.utils.data import DataLoader
import torch.multiprocessing as mp

from preprocessing import customdataset
from nets.modules.bvp2abp import bvp2abp
from nets.modules.unet import Unet
from train import train

import json
import numpy as np
import h5py
import matplotlib.pyplot as plt

with open('config/parameter.json') as f:
    json_data = json.load(f)
    param = json_data.get("parameters")
    channels = json_data.get("parameters").get("in_channels")
    out_channels = json_data.get("parameters").get("out_channels")
    hyper_param = json_data.get("hyper_parameters")
    wb = json_data.get("wandb")
    root_path = json_data.get("parameters").get("root_path")  # mimic uci containing folder
    data_path = json_data.get("parameters").get("dataset_path")  # raw mimic uci selection
    sampling_rate = json_data.get("parameters").get("sampling_rate")
    models = json_data.get("parameters").get("models")
    cases = json_data.get("parameters").get("cases")

print(sys.version)

# GPU Setting
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print('----- GPU INFO -----\nDevice:', DEVICE)  # 출력결과: cuda
print('Count of using GPUs:', torch.cuda.device_count())
print('Current cuda device:', torch.cuda.current_device())
gpu_ids = list(map(str, list(range(torch.cuda.device_count()))))
total_gpu_memory = 0
for gpu_id in gpu_ids:
    total_gpu_memory += torch.cuda.get_device_properties("cuda:" + gpu_id).total_memory
print('Total GPU Memory :', total_gpu_memory, '\n--------------------')

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(125)
    cudnn.enabled = True
    cudnn.benchmark = False
    cudnn.deterministic = True
else:
    torch.manual_seed(125)
    print("cuda not available")


def main(model_name, model_case, dataset_name, in_channel, cross_val=1, fft=1):
    samp_rate = sampling_rate["60"]
    channel = channels[in_channel]
    read_path = root_path + data_path[dataset_name][1]
    # TODO use hdf5 file for training Done
    if model_name is 'BPNet':
        model = bvp2abp(in_channels=channel[0], out_channels=out_channels, case=model_case[0], fft=fft)
        model.share_memory()
        train_filename = read_path + 'case(P+V+A)_' + str(param['chunk_size']) + '_train(cv' + \
                         str(cross_val) + ').hdf5'
        test_filename = read_path + 'case(P+V+A)_' + str(param['chunk_size']) + '_test.hdf5'
        # TODO make dataset loader function in train_utils
        if os.path.isfile(train_filename) and os.path.isfile(test_filename):
            '''train dataset load'''
            with h5py.File(train_filename, "r") as train_f:
                print(train_filename)
                train_ple, train_abp, train_size = np.array(train_f['train/ple/0']), np.array(
                    train_f['train/abp/0']), np.array(train_f['train/size/0'])
                train_dataset = customdataset.CustomDataset(x_data=train_ple, y_data=train_abp, size_factor=train_size)
                '''loader에 pin_memory=True를 주면 GPU 메모리를 더 효율적으로 사용할 수 있음
                https://gaussian37.github.io/dl-pytorch-snippets/#%EB%B2%A1%ED%84%B0%EC%99%80-%ED%85%90%EC%84%9C%EC%9D%98-element-wise-multiplication-1
                '''
                train_loader = DataLoader(train_dataset, batch_size=hyper_param["batch_size"], shuffle=True)
                val_ple, val_abp, val_size = np.array(train_f['validation/ple/0']), np.array(
                    train_f['validation/abp/0']), np.array(train_f['validation/size/0'])
                val_dataset = customdataset.CustomDataset(x_data=val_ple, y_data=val_abp, size_factor=val_size)
                val_loader = DataLoader(val_dataset, batch_size=hyper_param["batch_size"], shuffle=True)

            '''test dataset load'''
            with h5py.File(test_filename, "r") as test_f:
                print(test_filename)
                test_ple, test_abp, test_size = np.array(test_f['ple']), np.array(test_f['abp']), np.array(
                    test_f['size'])
                test_dataset = customdataset.CustomDataset(x_data=test_ple, y_data=test_abp, size_factor=test_size)
                test_loader = DataLoader(test_dataset, batch_size=hyper_param["batch_size"], shuffle=True)
        else:
            print("No such file or directory, creating new dataset...")
            import vid2bp.preprocessing.dataset_selector as ds
            ds.selector(model_name, dataset_name, channel, samp_rate, cv=cross_val)
            with h5py.File(train_filename, "r") as train_f:
                print(train_filename)
                train_ple, train_abp, train_size = np.array(train_f['train/ple/0']), np.array(
                    train_f['train/abp/0']), np.array(train_f['train/size/0'])
                train_dataset = customdataset.CustomDataset(x_data=train_ple, y_data=train_abp, size_factor=train_size)
                train_loader = DataLoader(train_dataset, batch_size=hyper_param["batch_size"], shuffle=True)
                val_ple, val_abp, val_size = np.array(train_f['validation/ple/0']), np.array(
                    train_f['validation/abp/0']), np.array(train_f['validation/size/0'])
                val_dataset = customdataset.CustomDataset(x_data=val_ple, y_data=val_abp, size_factor=val_size)
                val_loader = DataLoader(val_dataset, batch_size=hyper_param["batch_size"], shuffle=True)

            '''test dataset load'''
            with h5py.File(test_filename, "r") as test_f:
                print(test_filename)
                test_ple, test_abp, test_size = np.array(test_f['ple']), np.array(test_f['abp']), np.array(
                    test_f['size'])
                test_dataset = customdataset.CustomDataset(x_data=test_ple, y_data=test_abp, size_factor=test_size)
                test_loader = DataLoader(test_dataset, batch_size=hyper_param["batch_size"], shuffle=False)

    elif model_name is 'Unet':
        model = Unet(in_channels=channel[0])
        train_filename = read_path + 'case(' + str(channel[-1]) + ')_' + \
                         str(int(param['chunk_size'] / 125) * samp_rate) + '_train(cv' + str(cross_val) + ')256.hdf5'
        test_filename = read_path + 'case(' + str(channel[-1]) + ')_' + \
                        str(int(param['chunk_size'] / 125) * samp_rate) + '_test256.hdf5'
        print(train_filename)
        print(test_filename)
        if os.path.isfile(train_filename) and os.path.isfile(test_filename):
            '''train dataset load'''
            with h5py.File(train_filename, "r") as train_f:
                train_ple, train_abp = np.array(train_f['train/ple/0']), np.array(train_f['train/abp/0'])
                train_dataset = customdataset.CustomDataset_Unet(x_data=train_ple, y_data=train_abp)
                train_loader = DataLoader(train_dataset, batch_size=hyper_param["batch_size"], shuffle=True)

            '''test dataset load'''
            with h5py.File(test_filename, "r") as test_f:
                test_ple, test_abp = np.array(test_f['ple']), np.array(test_f['abp'])
                test_dataset = customdataset.CustomDataset_Unet(x_data=test_ple, y_data=test_abp)
                test_loader = DataLoader(test_dataset, batch_size=hyper_param["batch_size"], shuffle=True)
        else:
            print("No such file or directory creating new dataset")
            import vid2bp.preprocessing.dataset_selector as ds
            ds.selector(model_name, dataset_name, channel, samp_rate, cv=cross_val)
            with h5py.File(train_filename, "r") as train_f:
                print(train_filename)
                train_ple, train_abp = np.array(train_f['ple']), np.array(train_f['abp'])
                train_dataset = customdataset.CustomDataset_Unet(x_data=train_ple, y_data=train_abp)
                train_loader = DataLoader(train_dataset, batch_size=hyper_param["batch_size"], shuffle=True)

            '''test dataset load'''
            with h5py.File(test_filename, "r") as test_f:
                print(test_filename)
                test_ple, test_abp = np.array(test_f['ple']), np.array(test_f['abp'])
                test_dataset = customdataset.CustomDataset_Unet(x_data=test_ple, y_data=test_abp)
                test_loader = DataLoader(test_dataset, batch_size=hyper_param["batch_size"], shuffle=True)

    else:
        raise ValueError("** model name is not correct, please check supported model name in parameter.json **")
    '''model train'''
    train(model_n=model_name, model=model, case=model_case[-1],fft=fft, dataset_name=dataset_name, in_channel=channel,
          device=DEVICE,
          train_loader=train_loader, validation_loader=val_loader, test_loader=test_loader,
          epochs=hyper_param["epochs"])


def run_all():
    model_cases = [cases['Total'], cases['Trend'], cases['Detail']]
    channel_case = ['second']
    fft_case = [1, 0]
    for channel in channel_case:
        for case in reversed(model_cases):
            for fft in fft_case:
                if channel == 'zeroth' and (case == cases['Detail'] or case == cases['Total']):
                    continue
                else:
                    print("channel : ", channel, "case : ", case, "fft : ", fft)
                    main(model_name="BPNet", model_case=case, dataset_name='uci', in_channel=channel, cross_val=1, fft=fft)
                # try:
                #     main(model_name="BPNet", model_case=case, dataset_name='uci', in_channel=channel, cross_val=1)
                # except RuntimeError as e:
                #     print(e)
                #     continue  # skip this case


if __name__ == '__main__':
    # main(model_name="Unet", dataset_name="uci_unet", in_channel='zero', cross_val=1)
    # main(model_name="BPNet", model_case=2, dataset_name="uci", in_channel='zeroth', cross_val=1)
    # run_all()
    # try:
    #     mp.set_start_method('spawn', force=True)
    # except RuntimeError:
    #     pass

    # main(model_name="BPNet", model_case=cases['Total'], dataset_name="uci", in_channel='zeroth', cross_val=1)

    # run_all()
    # main(model_name="BPNet", model_case=cases['Total'], dataset_name="uci", in_channel='first', cross_val=1, fft=1)
    # main(model_name="BPNet", model_case=cases['Total'], dataset_name="uci", in_channel='first', cross_val=1, fft=0)
    # main(model_name="BPNet", model_case=cases['Detail'], dataset_name="uci", in_channel='second', cross_val=1, fft=1)
    # main(model_name="BPNet", model_case=cases['Detail'], dataset_name="uci", in_channel='second', cross_val=1, fft=0)
    # main(model_name="BPNet", model_case=cases['Trend'], dataset_name="uci", in_channel='second', cross_val=1, fft=1)
    # main(model_name="BPNet", model_case=cases['Trend'], dataset_name="uci", in_channel='second', cross_val=1, fft=0)
    main(model_name="BPNet", model_case=cases['Total'], dataset_name="uci", in_channel='second', cross_val=1, fft=1)
    # main(model_name="BPNet", model_case=cases['Total'], dataset_name="uci", in_channel='second', cross_val=1, fft=0)
