import torch
import torch.nn as nn
import torch.nn.functional as F


class PeakCNN(nn.Module):
    def __init__(self):
        super(PeakCNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2)  
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)  
        self.fc1 = nn.Linear(32 * 100, 128)  
        self.fc2 = nn.Linear(128, 100)  

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 32 * 100) 
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = x.view(-1, 1, 100)  
        return x