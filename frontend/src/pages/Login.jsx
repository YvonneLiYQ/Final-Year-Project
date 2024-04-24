import React from "react"
import { useNavigate } from "react-router-dom";
import { Form, Input, message } from "antd"
import axios from "axios";
import style from "./Login.module.css"



export default function ReviewPage() {
    const navigate = useNavigate();

    function goToRegister(){
        navigate('/register');
    }

    const onFinish = (values) => {
        axios.get(`/api/user?username=${values.username}&password=${values.password}`).then(res => {
            if(res.data[0]?.id){
                localStorage.setItem('id', res.data[0].id);
                localStorage.setItem('username', values.username);
                // 登录成功
                navigate('/');
            }else{
                message.error('Login failed')
            }
        })
    };
    const onFinishFailed = (errorInfo) => {
        message.error('Failed:', errorInfo);
    };

    return <div className={style.loginWrapper}>
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
                <button htmlType="submit">
                    Login
                </button>
                <span className={style.registerText} onClick={goToRegister}>Register</span>
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