import matplotlib
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
matplotlib.use('Agg')
import time
import numpy as np
import cv2 as cv
from dataset import BGRtoRGB
import torch
from torch.optim import Adam
from torch.utils.data import DataLoader
from dataset import PreprocessDataset, denorm
from model import Model


def main():
    epochs = 20  # 总共迭代几次
    restore_epochs = 0  # 从第几次恢复训练
    batch_size = 20  # 每个批次的大小，如果报了显存错误，调小即可
    gpu = 0  # gpu=-1表示用cpu跑 
    fast_train = True  # 是否使用快速训练
    learning_rate = 5e-5  # 学习率
    save_interval = 300  # 每隔几个iter保存一次结果图和权重
    train_content_dir = r'content'  # 内容图存放的文件夹
    train_style_dir = r'style'  # 风格图存放的文件夹
    test_content_dir = train_content_dir
    test_style_dir = train_style_dir
    save_weight_name = r'decoder.pth'  # 断点续训。为None时不续训，相当于运行此程序时从0开始训练
    # 创建文件夹
    model_state_dir = 'checkpoint'  # 权重保存路径
    image_dir = 'result_images'  # 输出图片保存路径
    #   创建文件夹
    os.makedirs(model_state_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    # 选择用哪个gpu，若没gpu则用cpu
    if torch.cuda.is_available() and gpu >= 0:
        device = torch.device('cuda:%s' % gpu)
        print('使用GPU:%s' % torch.cuda.get_device_name(0))
    else:
        device = 'cpu'

    print('epochs:%s' % epochs)
    print('restore_epochs:%s' % restore_epochs)
    print('batch_size:%s' % batch_size)
    print('lr:%s' % learning_rate)

    # 数据预处理
    train_dataset = PreprocessDataset(train_content_dir, train_style_dir)
    test_dataset = PreprocessDataset(test_content_dir, test_style_dir)

    print('train_dataset:', len(train_dataset), 'test_dataset:', len(test_dataset))
    # 加载数据集
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=5, shuffle=False)

    # 搭建模型
    model = Model().to(device)
    if save_weight_name is not None:
        try:
            model.load_state_dict(torch.load(save_weight_name))  # 加载权重
            print('断点续训...')
        except:
            print('权重未加载，重新训练...')
    optimizer = Adam(model.parameters(), lr=learning_rate)  # 搭建优化器
    scaler = torch.cuda.amp.GradScaler()  # 梯度缩放
    print('开始训练，请耐心等待。。。')
    # 训练
    t = time.time()
    loss_list = []
    for epoch in range(0, epochs):
        epoch += restore_epochs
        for i, (content, style) in enumerate(train_loader):
            content = content.to(device)
            style = style.to(device)
            if fast_train:
                with torch.cuda.amp.autocast():
                    loss = model(content, style)
                    optimizer.zero_grad()  # 梯度归零
                    scaler.scale(loss).backward()  # 梯度缩放
                    scaler.step(optimizer)  # 反向传播
                    scaler.update()  # 更新
            else:
                loss = model(content, style)
                optimizer.zero_grad()  # 梯度归零
                loss.backward()  # 反向传播
                optimizer.step()  # 更新
            loss_list.append(loss.item())

            if i % save_interval == 0:  # 每隔几个iter保存一次结果
                content, style = next(iter(test_loader))  # iter不能写到前面，否则会迭代完
                content = content.to(device)
                style = style.to(device)
                with torch.no_grad():
                    out = model.generate(content, style)  # 得到迁移结果图
                content = denorm(content, device)  # (b,c,h,w) b是批次，c是图片通道，h是图片高，w是图片宽
                style = denorm(style, device)  # (b,c,h,w)
                out = denorm(out, device)  # (b,c,h,w)
                # 存图
                content = content.permute(0, 2, 3, 1)  # (b,h,w,c)
                style = style.permute(0, 2, 3, 1)  # (b,h,w,c)
                out = out.permute(0, 2, 3, 1)  # (b,h,w,c)
                res = torch.cat([content, style, out], dim=2)  # (b,h,3*w,c)
                b, h, w, c = res.shape
                res = res.view(b * h, w, c).cpu().numpy()  # (b*h,3*w,c)
                res = BGRtoRGB((res * 255.).astype('uint8'))  # 以RGB读图的，所以需要转回RGB存图
                # print(res.shape, res.min(), res.max())
                cv.imwrite('%s/epoch%s_iter%s.png' % (image_dir, epoch + 1, i + 1), res)
                torch.save(model.state_dict(), 'decoder.pth')  # 保存权重
                print('epoch%s_iter%s loss:%s cost:%s' % (
                    epoch + 1, i + 1, np.round(np.mean(loss_list), 6), np.round(time.time() - t, 4)), end='')
                print('  %s/epoch%s_iter%s:已保存权重:%s' % (image_dir, epoch + 1, i + 1, save_weight_name))
                t = time.time()  # 更新时间

        if epoch >= epochs:
            print('已训练完')
            torch.save(model.state_dict(), 'decoder.pth')  # 保存权重
            break


if __name__ == '__main__':
    main()
