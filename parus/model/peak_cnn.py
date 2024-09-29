import torch
import torch.nn as nn
import torch.nn.functional as F


class PeakCNN(nn.Module):
    def __init__(self):
        super(PeakCNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=5, stride=1, padding=2)  
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)  
        self.fc1 = nn.Linear(32 * 300, 128)  
        self.fc2 = nn.Linear(128, 300)  
        self.dropout = nn.Dropout(0.2)
        self.bn1 = nn.BatchNorm1d(16)
        self.bn2 = nn.BatchNorm1d(32)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.bn1(x)
        x = F.relu(self.conv2(x))
        x = self.bn2(x)
        x = x.view(-1, 32 * 300) 
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        x = x.view(-1, 1, 300)  
        return x
