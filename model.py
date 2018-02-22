import torch
import torch.nn as nn
from math import sqrt


class Net(torch.nn.Module):
    def __init__(self, n_channels, d=32, s=6, m=4):
        super(Net, self).__init__()

        # Feature extraction
        self.first_part = nn.Sequential(nn.Conv2d(in_channels=n_channels, out_channels=d, kernel_size=5, stride=1, padding=2),
                                        nn.PReLU())

        self.layers = []
        # Shrinking
        self.layers.append(nn.Sequential(nn.Conv2d(in_channels=d, out_channels=s, kernel_size=1, stride=1, padding=0),
                                         nn.PReLU()))

        # Non-linear Mapping
        for _ in range(m):
            self.layers.append(nn.Conv2d(in_channels=s, out_channels=s, kernel_size=3, stride=1, padding=1))
        self.layers.append(nn.PReLU())

        # Expanding
        self.layers.append(nn.Sequential(nn.Conv2d(in_channels=s, out_channels=d, kernel_size=1, stride=1, padding=0),
                                         nn.PReLU()))

        self.mid_part = torch.nn.Sequential(*self.layers)

        # Deconvolution
        self.last_part = nn.ConvTranspose2d(in_channels=d, out_channels=n_channels, kernel_size=9, stride=2, padding=5, output_padding=0)

    def forward(self, x):
        out = self.first_part(x)
        out = self.mid_part(out)
        out = self.last_part(out)
        return out

    def weight_init(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
                m.weight.data.normal_(0.0, sqrt(2/m.out_channels/m.kernel_size[0]/m.kernel_size[0]))
                if m.bias is not None:
                    m.bias.data.zero_()