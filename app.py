from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from PIL import Image
import os
from sql import BarcodeDatabase
import base64
from datetime import datetime

# 获取当前日期和时间
now = datetime.now()
# 格式化为 '年月日时分'
formatted_date_time = now.strftime("%Y%m%d%H%M")
today = datetime.today()
formatted_date = today.strftime("%Y%m%d")

# 数据库配置
db_config = {
    'host': '',
    'user': 'root',
    'password': '',
    'dbname': ''
}

# 创建 Flask 应用实例
app = Flask(__name__)

# 获取 app.py 文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 使用 os.path.join() 方法，确保 UPLOAD_FOLDER 在 app.py 同目录下
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
# 设置允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 配置应用，指定文件上传的目录
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 检查文件名是否安全且符合允许的扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 解码图片中的条形码，并返回条形码类型和数据的列表
def decode_barcode(image_path):
    image = Image.open(image_path)
    decoded_objects = decode(image)
    barcodes = []
    for obj in decoded_objects:
        if obj.type == "CODE128":
            barcode_data = obj.data.decode('utf-8')
            barcode_type = obj.type
            barcodes.append((barcode_type, barcode_data))
    return barcodes

# 添加路由来提供存储在 UPLOAD_FOLDER 中的文件
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 添加路由来处理文件上传
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 检查 POST 请求中是否包含文件
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # 如果没有文件名，即用户没有选择文件，重定向回上传页面
        if file.filename == '':
            return redirect(request.url)
        # 如果文件是允许的类型，保存文件并解码条形码
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            barcodes = decode_barcode(save_path)
            # 检查是否识别到条形码
            if not barcodes:
                # 没有识别到条形码，显示错误消息
                error_message = 'No CODE128 barcodes detected in the image. Please try another image.'
                return render_template('upload.html', error_message=error_message)
            db = BarcodeDatabase(**db_config)
            db.insert_barcode_data(str(barcodes[0][1]), save_path, str(formatted_date), str(formatted_date_time))
            db.close()
            # 返回结果页面，并提供条形码数据和图片文件名
            return render_template('results.html', barcodes=barcodes, image_file=filename)
    # 如果是 GET 请求或者 POST 请求但文件不符合要求，显示上传表单
    return render_template('upload.html')

@app.route('/records')
def show_records():
    db = BarcodeDatabase(**db_config)
    data = db.get_all_data()
    db.close()

    # 将图片的二进制数据编码为 Base64
    encoded_records = []
    for record in data:
        danhao, photo, paisong, dizhi, riqi, charushijian = record
        photo_encoded = base64.b64encode(photo).decode('utf-8')  # 编码为 Base64 字符串
        encoded_records.append((danhao, photo_encoded, paisong, dizhi, riqi, charushijian))

    return render_template('records.html', records=encoded_records)

# 应用启动入口
if __name__ == '__main__':
    # 如果上传文件夹不存在，则创建该文件夹
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # 启动 Flask 应用（在调试模式下）
    app.run(debug=True, host='0.0.0.0')