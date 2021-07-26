import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
import numpy as np

class bvpdataset(Dataset):
    def __init__(self, A, M, T):
        self.transform = transforms.Compose([transforms.ToTensor()])
        self.a = A
        self.m = M
        self.label = T.reshape(-1, 1)

    def __getitem__(self, index):
        if torch.is_tensor(index):
            index = index.tolist()

        appearance_img = torch.tensor(np.transpose(self.a[index], (2, 0, 1)), dtype=torch.float32)
        mot_img = torch.tensor(np.transpose(self.m[index], (2, 0, 1)), dtype=torch.float32)
        label = torch.tensor(self.label[index], dtype=torch.float32)

        return appearance_img, mot_img, label

    def __len__(self):
        return len(self.label)