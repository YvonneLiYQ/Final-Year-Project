import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import vgg16
import torch



def calc_mean_std(features):  # 输入(b,c,h,w) 计算空间维度的mean和std
    batch_size, c = features.size()[:2]
    features_mean = features.reshape(batch_size, c, -1).mean(dim=2).reshape(batch_size, c, 1, 1)
    features_std = features.reshape(batch_size, c, -1).std(dim=2).reshape(batch_size, c, 1, 1) + 1e-7  # 加个误差是防止除以0
    return features_mean, features_std  # 为常数
 

def adain(content_features, style_features):  # (b,c,h,w)
    content_mean, content_std = calc_mean_std(content_features)  # 计算内容图的mean和std
    style_mean, style_std = calc_mean_std(style_features)  # 计算风格图的mean和std
    normalized_features = style_std * (content_features - content_mean) / content_std + style_mean
    return normalized_features  # (b,c,h,w)   内容图标准化后，再用风格图的mean和std反标准化


class VGGEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = vgg16(pretrained=True)
        # print(vgg)
        # vgg.load_state_dict(torch.load(r'vgg19-dcbb9e9d.pth'))  # 加载VGG19权重
        vgg = vgg.features
        # 选层可以自己选，效果也不同
        ##用于vgg16
        self.s1 = vgg[: 2]  # inputs->b1_c1  第一个块(block)的第一层卷积层(conv)，下面以此类推
        self.s2 = vgg[2: 7]  # b1_c1->b2_c1
        self.s3 = vgg[7: 12]  # b2_c1->b3_c1
        self.s4 = vgg[12: 19]  # b3_c1->b4_c1

        for p in self.parameters():
            p.requires_grad = False  # 所有参数设为不可训练

    def forward(self, inputs, output_last_feature=False):  # 选取中间层还是最后一层
        s1 = self.s1(inputs)
        s2 = self.s2(s1)
        s3 = self.s3(s2)
        s4 = self.s4(s3)
        # s5 = self.s5(s4)
        if output_last_feature:
            return s4
        else:
            return s1, s2, s3, s4

class RC(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, pad_size=1, activated=True):
        super().__init__()
        self.pad = nn.ReflectionPad2d((pad_size, pad_size, pad_size, pad_size))  # 折射填充，和0填充一样的用法，只是填充的数值不同而已
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size)
        self.activated = activated

    def forward(self, inputs):
        h = self.pad(inputs)
        h = self.conv(h)
        if self.activated:
            return F.relu(h)
        else:
            return h


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.rc1 = RC(512, 256, 3, 1)
        self.rc2 = RC(256, 256, 3, 1)
        self.rc3 = RC(256, 256, 3, 1)
        self.rc4 = RC(256, 256, 3, 1)
        self.rc5 = RC(256, 128, 3, 1)
        self.rc6 = RC(128, 128, 3, 1)
        self.rc7 = RC(128, 64, 3, 1)
        self.rc8 = RC(64, 64, 3, 1)
        self.rc9 = RC(64, 3, 3, 1, False)

    def forward(self, features):  # (b,512,h,w)   (b,c,h,w)
        h = self.rc1(features)
        h = F.interpolate(h, scale_factor=2)
        h = self.rc2(h)
        h = self.rc3(h)
        h = self.rc4(h)
        h = self.rc5(h)
        h = F.interpolate(h, scale_factor=2)
        h = self.rc6(h)
        h = self.rc7(h)
        h = F.interpolate(h, scale_factor=2)
        h = self.rc8(h)
        h = self.rc9(h)  # (b,3,800,600)   (b,c,h,w)
        return h


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.vgg_encoder = VGGEncoder()
        self.decoder = Decoder()

    def generate(self, content_images, style_images, alpha=1.0):  # 把内容图和风格图用VGG编码，然后送入adain，然后送入解码器，得到结果图
        content_features = self.vgg_encoder(content_images, output_last_feature=True)  # (b,512,h,w)
        style_features = self.vgg_encoder(style_images, output_last_feature=True)  # (b,512,h,w)
        # print('content_features:',content_features.shape,'style_features:',style_features.shape)
        t = adain(content_features, style_features)  # (b,512,h,w) t是标准化后的特征
        # print(t.shape)
        t = alpha * t + (1 - alpha) * content_features  # t是反标准化后的特征
        out = self.decoder(t)  # (1,3,800,600)
        # print(out.shape)
        return out

    # @staticmethod
    def calc_content_loss(self, out_features, t):
        return F.mse_loss(out_features, t)

    # @staticmethod
    def calc_style_loss(self, content_middle_features, style_middle_features):
        loss = 0
        for c, s in zip(content_middle_features, style_middle_features):
            c_mean, c_std = calc_mean_std(c)
            s_mean, s_std = calc_mean_std(s)
            loss += F.mse_loss(c_mean, s_mean) + F.mse_loss(c_std, s_std)
        return loss

    def forward(self, content_images, style_images, alpha=1.0, lam=10):
        content_features = self.vgg_encoder(content_images, output_last_feature=True)
        style_features = self.vgg_encoder(style_images, output_last_feature=True)
        t = adain(content_features, style_features)
        t = alpha * t + (1 - alpha) * content_features
        out = self.decoder(t)  # out是结果图

        output_features = self.vgg_encoder(out, output_last_feature=True)  # 结果图再次输入VGG，风格图也输入VGG，特征做损失函数
        output_middle_features = self.vgg_encoder(out, output_last_feature=False)
        style_middle_features = self.vgg_encoder(style_images, output_last_feature=False)

        loss_c = self.calc_content_loss(output_features, t)  # 结果图特征和反标准化后的特征做内容损失
        loss_s = self.calc_style_loss(output_middle_features, style_middle_features)  # 结果图多层特征和风格图多层特征依次做风格损失
        loss = loss_c + lam * loss_s
        return loss


def main():
    model = VGGEncoder()
    x = torch.rand([10, 3, 224, 224])
    y_pred = model(x, output_last_feature=True)
    print(y_pred.shape)


if __name__ == '__main__':
    main()
