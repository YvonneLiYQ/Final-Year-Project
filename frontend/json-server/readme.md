// 全局安装 json-server，已安装过则不用执行此命令
npm install json-server -g

// 开启 json-server 服务，指定端口 3001
json-server db.json --watch --port 3001
