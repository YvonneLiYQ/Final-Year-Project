
import os
import io
import base64
import torch
from flask import Flask, request, jsonify
from torchvision import transforms
from model import Model
import cv2 as cv
from dataset import BGRtoRGB
from PIL import Image
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

upload_folder = 'uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])  # 归一化

trans = transforms.Compose([transforms.ToTensor(),
                            normalize])


def denorm(tensor, device):  # 反归一化，用于显示
    std = torch.Tensor([0.229, 0.224, 0.225]).reshape(-1, 1, 1).to(device)
    mean = torch.Tensor([0.485, 0.456, 0.406]).reshape(-1, 1, 1).to(device)
    res = torch.clamp(tensor * std + mean, 0, 1)
    return res


def main(content,style):
    gpu = 0  # gpu=-1表示用cpu跑
    #content = r'test_img/6.jpg'  # 你的内容图路径
    #style = r'style_valdata/a.y.-jackson_algoma-in-november-1935 13.51.07.jpg'  # 你的风格图路径
    alpha = 0.4  # 超参数，官方默认是1。越大表示风格的比重越大
    save_weight_name = r'decoder.pth'  # 断点续训。为None时不续训，相当于运行此程序时从0开始训练
    # 选择用哪个gpu，若没gpu则用cpu
    if torch.cuda.is_available() and gpu >= 0:
        device = torch.device('cuda:%s' % gpu)
        print('使用GPU:%s' % torch.cuda.get_device_name(0))
    else:
        device = 'cpu'

    # 搭建网络
    model = Model()
    model.eval()
    if save_weight_name is not None:
        model.load_state_dict(torch.load(save_weight_name, map_location=lambda storage, loc: storage))
    model = model.to(device)

    c = BGRtoRGB(cv.imread(content))  # 转为RGB图像
    s = BGRtoRGB(cv.imread(style))
    c_tensor = trans(c).unsqueeze(0).to(device)  # 图像归一化
    s_tensor = trans(s).unsqueeze(0).to(device)
    with torch.no_grad():
        out = model.generate(c_tensor, s_tensor, alpha)  # out是输出的结果图

    out = denorm(out, device)

    out = BGRtoRGB(out.cpu().numpy().squeeze(0).transpose([1, 2, 0]) * 255).astype('uint8')

    save_name = '%s_%s.png' % (os.path.basename(content).split('.')[0], os.path.basename(style).split('.')[0])
    cv.imwrite(save_name, out)

    return save_name

@app.route('/submit', methods=['POST'])
def submit():
    try:
        content_image = request.files.get('content')
        style_image = request.files.get('style')

        if not content_image or not style_image:
            return jsonify({'error': 'Missing content or style image'}), 400

        content_filename = secure_filename(content_image.filename)
        style_filename = secure_filename(style_image.filename)

        content_file_path = os.path.join(upload_folder, content_filename)
        style_file_path = os.path.join(upload_folder, style_filename)

        content_image.save(content_file_path)
        style_image.save(style_file_path)

        result_image = main(content_file_path, style_file_path)
        with open(result_image, 'rb') as f:
            encoded_img = base64.b64encode(f.read()).decode('ascii')

        return jsonify({"result": "data:image/png;base64," + encoded_img})
    except Exception as e:
        app.logger.error('Unhandled exception', exc_info=True)
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
