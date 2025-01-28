import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision.io import read_image
import sys
import argparse
from torch.serialization import add_safe_globals

# Allow the Net class to be safely loaded
add_safe_globals([Net])

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--model-path', type=str,
                        required=False, default='mnist_cnn.pt')
    args = parser.parse_args()

    print('Loading model from:', args.model_path)
    model = torch.load( args.model_path)
    
    print('Loading image from:', args.input)

    device = torch.device("cpu") 
    img = read_image(args.input)
    img = img[None]
    img = img.type('torch.FloatTensor')

    output = model(img)
    prediction = torch.argmax(output)
    print('\nPrediction:', prediction)
