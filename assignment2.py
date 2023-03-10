# -*- coding: utf-8 -*-
"""Assignment2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IMcO7W5v3uXNxQSGRH322FH8YPdptNXH

##Loading Libraries
"""

from google.colab import drive
drive.mount('/content/drive')

import torch
import torch.nn.functional as F
import torch.nn as nn
from tqdm import tqdm
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
from torch.autograd import Variable
import pandas as pd
ROOTDIR = "/content/drive/MyDrive/dataset"
VALDIR = "/content/drive/MyDrive/val_dataset/dataset"

"""## Dataloader"""

class Create_Dataset(Dataset):
    def __init__(self, rootdir,x_filenames, y_filenames):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.rootdir = rootdir
        self.x_filenames = x_filenames
        self.y_filenames = y_filenames

    def __len__(self):
        return len(self.x_filenames)

    def __getitem__(self, idx):
        spec_path = self.x_filenames[idx]
        label_path = self.y_filenames[idx]
        spec = np.load(os.path.join(self.rootdir,'X',spec_path))
        label = np.load(os.path.join(self.rootdir,'Y',label_path))
        label = np.sum(label,axis=1)
        label = (label>0)
        sample = {'spec': spec, 'label': label}
        return sample

def dataloader(ROOT,x_file_names, y_file_names, batchsize, num_workers):
    data = Create_Dataset(ROOT,x_file_names,y_file_names)
    data_loader = DataLoader(data, batch_size=batchsize,num_workers=num_workers,
                                              pin_memory=False)
    return data_loader

"""## Network Architecture

### RNN
"""

class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, self.hidden_size, self.num_layers, batch_first=True, dropout=0.2)
        #self.gru = nn.GRU(input_size, self.hidden_size, self.num_layers, batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_size, int(hidden_size/2))
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(int(hidden_size/2), int(hidden_size/2))
        self.fc3 = nn.Linear(int(hidden_size/2), num_classes)
    
    def forward(self, x):
        x = x.float()
        h0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size).float()).cuda() 
        c0 = Variable(torch.zeros(self.num_layers, x.size(0), self.hidden_size).float()).cuda()
        out, _ = self.lstm(x, (h0,c0)) 
        out = self.relu(self.fc1(out[:, -1, :]))
        out = self.relu(self.fc2(out))
        out = self.fc3(out) 
        return out

"""### VGG 16"""

class VGG16(nn.Module):
    def __init__(self, num_classes=10):
        super(VGG16, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU())
        self.layer2 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(), 
            nn.MaxPool2d(kernel_size = 2, stride = 2))
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU())
        self.layer4 = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size = 2, stride = 2))
        self.layer5 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU())
        self.layer6 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU())
        self.layer7 = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size = 2, stride = 2))
        self.layer8 = nn.Sequential(
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU())
        self.layer9 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU())
        self.layer10 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size = 2, stride = 2))
        self.layer11 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU())
        self.layer12 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU())
        self.layer13 = nn.Sequential(
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size = 2, stride = 2))
        self.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(7*7*512, 4096),
            nn.ReLU())
        self.fc1 = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU())
        self.fc2= nn.Sequential(
            nn.Linear(4096, num_classes))
        
    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.layer5(out)
        out = self.layer6(out)
        out = self.layer7(out)
        out = self.layer8(out)
        out = self.layer9(out)
        out = self.layer10(out)
        out = self.layer11(out)
        out = self.layer12(out)
        out = self.layer13(out)
        out = out.reshape(out.size(0), -1)
        out = self.fc(out)
        out = self.fc1(out)
        out = self.fc2(out)
        return out

"""### Dense network"""

# define the network class
class MyNetwork(nn.Module):
    def __init__(self):
        # call constructor from superclass
        super().__init__()
        
        # define network layers
        self.fc1 = nn.Linear(64000, 16000)
        # self.fc2 = nn.Linear(32000, 16000)
        self.fc3 = nn.Linear(16000, 4000)
        # self.fc4 = nn.Linear(8000, 4000)
        self.fc5 = nn.Linear(4000,1024)
        # self.fc6 = nn.Linear(2000,1024)
        self.fc7 = nn.Linear(1024,512)
        self.fc8 = nn.Linear(512,11)
        
    def forward(self, x):
        # define forward pass
        x = F.relu(self.fc1(x))
        # x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        # x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        # x = F.relu(self.fc6(x))
        x = F.relu(self.fc7(x))
        x = F.sigmoid(self.fc8(x))
        return x

# print model architecture
def print_size(net):
    """
    Print the number of parameters of a network
    """

    if net is not None and isinstance(net, torch.nn.Module):
        module_parameters = filter(lambda p: p.requires_grad, net.parameters())
        params = sum([np.prod(p.size()) for p in module_parameters])
        print("{} Parameters: {:.6f}M".format(
            net.__class__.__name__, params / 1e6), flush=True)

"""### Resnet"""

class Bottleneck(nn.Module):
    expansion = 4
    def __init__(self, in_channels, out_channels, i_downsample=None, stride=1):
        super(Bottleneck, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        self.batch_norm1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.batch_norm2 = nn.BatchNorm2d(out_channels)
        
        self.conv3 = nn.Conv2d(out_channels, out_channels*self.expansion, kernel_size=1, stride=1, padding=0)
        self.batch_norm3 = nn.BatchNorm2d(out_channels*self.expansion)
        
        self.i_downsample = i_downsample
        self.stride = stride
        self.relu = nn.ReLU()
        
    def forward(self, x):
        identity = x.clone()
        x = self.relu(self.batch_norm1(self.conv1(x)))
        
        x = self.relu(self.batch_norm2(self.conv2(x)))
        
        x = self.conv3(x)
        x = self.batch_norm3(x)
        
        #downsample if needed
        if self.i_downsample is not None:
            identity = self.i_downsample(identity)
        #add identity
        x+=identity
        x=self.relu(x)
        
        return x

class Block(nn.Module):
    expansion = 1
    def __init__(self, in_channels, out_channels, i_downsample=None, stride=1):
        super(Block, self).__init__()
       

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, stride=stride, bias=False)
        self.batch_norm1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, stride=stride, bias=False)
        self.batch_norm2 = nn.BatchNorm2d(out_channels)

        self.i_downsample = i_downsample
        self.stride = stride
        self.relu = nn.ReLU()

    def forward(self, x):
      identity = x.clone()

      x = self.relu(self.batch_norm2(self.conv1(x)))
      x = self.batch_norm2(self.conv2(x))

      if self.i_downsample is not None:
          identity = self.i_downsample(identity)
      print(x.shape)
      print(identity.shape)
      x += identity
      x = self.relu(x)
      return x


        
        
class ResNet(nn.Module):
    def __init__(self, ResBlock, layer_list, num_classes, num_channels=3):
        super(ResNet, self).__init__()
        self.in_channels = 64
        
        self.conv1 = nn.Conv2d(num_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.batch_norm1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.max_pool = nn.MaxPool2d(kernel_size = 3, stride=2, padding=1)
        
        self.layer1 = self._make_layer(ResBlock, layer_list[0], planes=64)
        self.layer2 = self._make_layer(ResBlock, layer_list[1], planes=128, stride=2)
        self.layer3 = self._make_layer(ResBlock, layer_list[2], planes=256, stride=2)
        self.layer4 = self._make_layer(ResBlock, layer_list[3], planes=512, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1,1))
        self.fc = nn.Linear(512*ResBlock.expansion, num_classes)
        
    def forward(self, x):
        x = self.relu(self.batch_norm1(self.conv1(x)))
        x = self.max_pool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc(x)
        x = torch.sigmoid(x)
        return x
        
    def _make_layer(self, ResBlock, blocks, planes, stride=1):
        ii_downsample = None
        layers = []
        
        if stride != 1 or self.in_channels != planes*ResBlock.expansion:
            ii_downsample = nn.Sequential(
                nn.Conv2d(self.in_channels, planes*ResBlock.expansion, kernel_size=1, stride=stride),
                nn.BatchNorm2d(planes*ResBlock.expansion)
            )
            
        layers.append(ResBlock(self.in_channels, planes, i_downsample=ii_downsample, stride=stride))
        self.in_channels = planes*ResBlock.expansion
        
        for i in range(blocks-1):
            layers.append(ResBlock(self.in_channels, planes))
            
        return nn.Sequential(*layers)

        
        
def ResNet50(num_classes, channels=3):
    return ResNet(Bottleneck, [3,4,6,3], num_classes, channels)
    
def ResNet101(num_classes, channels=3):
    return ResNet(Bottleneck, [3,4,23,3], num_classes, channels)

def ResNet152(num_classes, channels=3):
    return ResNet(Bottleneck, [3,8,36,3], num_classes, channels)

"""##  Training loop"""

loss_function = nn.BCELoss()

if __name__=="__main__":
    batch_size = 48
    chkpoint_dir = "/content/drive/MyDrive/EE603_Assignment_2/chkpoints"
    chkpoint_iter = 10
    X_file_names = sorted(os.listdir(os.path.join(ROOTDIR,'X')))
    Y_file_names = sorted(os.listdir(os.path.join(ROOTDIR,'Y')))
    data_loader = dataloader(ROOT=ROOTDIR,x_file_names=X_file_names,
                             y_file_names=Y_file_names,batchsize=batch_size,
                             num_workers = 4)
    X_file_names_val = sorted(os.listdir(os.path.join(VALDIR,'X')))
    Y_file_names_val = sorted(os.listdir(os.path.join(VALDIR,'Y')))
    validation_loader = dataloader(ROOT=VALDIR, x_file_names=X_file_names_val,
                                   y_file_names=Y_file_names_val,batchsize=batch_size,
                                   num_workers = 2)
    print("Dataloader loaded!")
    print("Files in train data: ",len(data_loader)*batch_size)
    print("Files in val data: ",len(validation_loader)*batch_size)
    max_iter = 100
    # model = MyNetwork()
    model = ResNet50(11,channels=1)
    model = model.cuda()
    print("Model loaded!")
    print("Number of parameters in the model: ",print_size(model))
    optimizer = torch.optim.Adam(params=model.parameters(),lr=0.0001)
    print("Training started!")
    for iter in range(max_iter):
        Loss = []
        correct_pred = 0
        correct_pred_val = 0
        TP = 0
        TP_val = 0
        FP = 0
        FP_val = 0
        TN = 0
        TN_val = 0
        FN = 0
        FN_val = 0
        model.train()
        print("Iteration: ",iter)
        for batch in tqdm(data_loader):
            x = batch["spec"].cuda()
            y = batch["label"]
            y = y.float()
            y = y.cuda()
            pred = model(x)
            optimizer.zero_grad()
            loss = loss_function(pred,y)
            pred = (pred>0.5)
            correct_pred += torch.sum(pred==y)
            TP += torch.sum(torch.logical_and(pred,y))
            TN += torch.sum(torch.logical_and(torch.logical_not(pred),torch.logical_not(y)))
            FP += torch.sum(torch.logical_and(torch.logical_not(y),pred))
            FN += torch.sum(torch.logical_and(torch.logical_not(pred),y))
            loss.backward()
            optimizer.step()
            loss_cpu = loss.detach().cpu()
            Loss.append(loss_cpu)
        Loss = np.asarray(Loss)
        print("Loss after iteration {}: ".format(np.mean(Loss)))
        total_pred = 11*batch_size*len(data_loader)
        recall = TP.item()/(TP.item()+FN.item())
        precision = TP.item()/(TP.item()+FP.item())
        f1_score = (2 * precision * recall)/(precision+recall)
        Accuracy = (correct_pred.item())/total_pred
        print("---At iteration {}--Accuracy: {}----F1 score: {}----Recall: {}----Precision: {}".format(iter,Accuracy,f1_score,recall,precision))

        # Validation loop
        model.eval()
        for batch in tqdm(validation_loader):
            x = batch["spec"].cuda()
            y = batch["label"]
            y = y.float()
            y = y.cuda()
            pred = model(x)
            pred = (pred>0.5)
            correct_pred_val += torch.sum(pred==y)
            TP_val += torch.sum(torch.logical_and(pred,y))
            TN_val += torch.sum(torch.logical_and(torch.logical_not(pred),torch.logical_not(y)))
            FP_val += torch.sum(torch.logical_and(torch.logical_not(y),pred))
            FN_val += torch.sum(torch.logical_and(torch.logical_not(pred),y))
        recall_val = TP_val.item()/(TP_val.item()+FN_val.item())
        precision_val = TP_val.item()/(TP_val.item()+FP_val.item())
        f1_score_val = (2 * precision_val * recall_val)/(precision_val+recall_val)
        total_pred_val = 11*batch_size*len(validation_loader)
        val_accuracy = (correct_pred_val.item())/total_pred_val
        print("---At iteration {}--Accuracy: {}----F1 score: {}----Recall: {}----Precision: {}".format(iter,val_accuracy,f1_score_val,recall_val,precision_val))
        # if (iter%chkpoint_iter)==0:
        #     chk_file_path = os.path.join(chkpoint_dir,str(iter)+'.pt')
        #     torch.save(model.state_dict(),chk_file_path)
        #     print("Model saved after {} iterations".format(iter))

"""##To Create CSV File"""

class Create_Testset(Dataset):
    def __init__(self, rootdir,x_filenames):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.rootdir = rootdir
        self.x_filenames = x_filenames

    def __len__(self):
        return len(self.x_filenames)

    def __getitem__(self, idx):
        spec_path = self.x_filenames[idx]
        # filename = os.path.split(x_filenames[idx])
        spec = np.load(os.path.join(self.rootdir,'X',spec_path))
        sample = {'spec': spec,'fileid': self.x_filenames[idx]}
        return sample

def testloader(ROOT,x_file_names, batchsize, num_workers):
    data = Create_Testset(ROOT,x_file_names)
    test_loader = DataLoader(data, batch_size=batchsize,num_workers=num_workers,
                                              pin_memory=False)
    return test_loader

torch.save(model.state_dict(),"/content/drive/MyDrive/EE603_Assignment_2/best_checkpoint.pt")

"""##Test samples"""

TESTDIR="/content/drive/MyDrive/EE603_TEST_2/test"
# TESTDIR = VALDIR
X_file_names_tests = sorted(os.listdir(os.path.join(TESTDIR,'X')))
data_loader = testloader(ROOT=TESTDIR,x_file_names=X_file_names_tests,batchsize=batch_size,
        num_workers = 1)
        # Validation loop
model = ResNet50(11,channels=1)
chkpoint = torch.load("/content/drive/MyDrive/EE603_Assignment_2/best_checkpoint.pt")
model.load_state_dict(chkpoint)
model = model.cuda()
model.eval()
filenames = [] # name of files
classes = []  # name of classes
events_types = {
    0: 'Alarm_bell_ringing', 
    1: 'Blender', 
    2: 'Cat', 
    3: 'Dishes', 
    4: 'Dog',
    5: 'Electric_shaver_toothbrush', 
    6: 'Frying', 
    7: 'Running_water',
    8: 'Silence', 
    9: 'Speech', 
    10: 'Vacuum_cleaner'
}
for batch in tqdm(data_loader):
    x = batch["spec"].cuda()
    name = batch["fileid"]
    pred = model(x)
    pred = (pred>=0.4)
    for i in range(pred.shape[0]):
      string =''
      for j in range(pred.shape[1]):
        if pred[i][j]==1 and j!=8:
          string+=(events_types[j]+",")
      classes.append(string[:-1])
      filenames.append(name[i])


print(classes)
print(filenames)
df = {
    "fileid": filenames,
    "prediction": classes
}
df = pd.DataFrame(df)
df.to_csv('/content/drive/MyDrive/EE603_Assignment_2/prediction_on_val.csv')

"""##Code block below is useless and is for personal purpose only"""

arr = np.load("/content/drive/MyDrive/val_dataset/dataset/Y/eventroll_1171.npy")

arr = (np.sum(arr,axis=1))>0

# with torch.no_grad():
#     correct_pred = 0
#     correct_pred_val = 0
#     TP = 0
#     TP_val = 0
#     FP = 0
#     FP_val = 0
#     TN = 0
#     TN_val = 0
#     FN = 0
#     FN_val = 0
#     for batch in tqdm(validation_loader):
#         x = batch["spec"].cuda()
#         y = batch["label"]
#         y = y.float()
#         y = y.cuda()
#         pred = model(x)
#         pred = (pred>0.5)
#         correct_pred_val += torch.sum(pred==y)
#         TP_val += torch.sum(torch.logical_and(pred,y))
#         TN_val += torch.sum(torch.logical_and(torch.logical_not(pred),torch.logical_not(y)))
#         FP_val += torch.sum(torch.logical_and(torch.logical_not(y),pred))
#         FN_val += torch.sum(torch.logical_and(torch.logical_not(pred),y))
#     recall_val = TP_val.item()/(TP_val.item()+FN_val.item())
#     precision_val = TP_val.item()/(TP_val.item()+FP_val.item())
#     f1_score_val = (2 * precision_val * recall_val)/(precision_val+recall_val)
#     total_pred_val = 11*batch_size*len(validation_loader)
#     val_accuracy = (correct_pred_val.item())/total_pred_val
#     print("---At iteration {}--Accuracy: {}----F1 score: {}----Recall: {}----Precision: {}".format(iter,val_accuracy,f1_score_val,recall_val,precision_val))

cl = []
for i in range(11):
  if (arr[i])==1:
    cl.append(events_types[i])
print(cl)