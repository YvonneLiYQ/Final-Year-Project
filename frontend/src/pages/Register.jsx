import React from "react"
import { Form, Input, message } from "antd"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import style from "./Register.module.css"

export default function Register() {
    const navigate = useNavigate();

    const onFinish = (values) => {
        axios.post('/api/user', {
            username: values.username,
            password: values.password
        }).then(res => {
            // 注册成功，跳转到登陆页面。注册失败弹出错误提示
            if(res.data.id){
                navigate('/login')
            }else {
                message.error('注册失败')
            }
        })
    };
    const onFinishFailed = (errorInfo) => {
        message.log('Failed:', errorInfo);
    };

    return <div className={style.registerWrapper}>
         <Form
            className={style.form}
            name="basic"
            labelCol={{
                span: 8,
            }}
            wrapperCol={{
                span: 16,
            }}
            style={{
                maxWidth: 600,
            }}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete="off"
        >
            <Form.Item
            label="Username"
            name="username"
            rules={[
                {
                required: true,
                message: 'Please input your username!',
                },
            ]}
            >
            <Input />
            </Form.Item>

            <Form.Item
                label="Password"
                name="password"
                rules={[
                    {
                    required: true,
                    message: 'Please input your password!',
                    },
                ]}
                >
            <Input.Password />
            </Form.Item>
            <Form.Item
                wrapperCol={{
                    span: 16,
                }}
            >
                <button type="primary" htmlType="submit">
                    注册
                </button>
            </Form.Item>
        </Form>
        <div style={{position: "fixed", top: "30px"}}>
            <div className='image-section1'>
                <img src='/originPicture.jpg'/>
            </div>

            <div className='image-section2'>
                <img src='/afterTransfer.png'/>
            </div>

            <div className='main-word'>
            <h2>Creating joy</h2>
            <h3>Start uploading your images and changing styles</h3>
            </div>
        </div>
    </div>
}