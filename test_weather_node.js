// Node.js测试和风天气API
const https = require('https');

// 和风天气API密钥
const apiKey = "。。。";
// 使用北京的LocationID
const location = "101010100";

// 构建API URL
const url = `https://devapi.qweather.com/v7/weather/now?location=${location}&lang=zh`;

console.log("测试和风天气API:");
console.log(`请求URL: ${url}`);

// 发送请求
const options = {
    headers: {
        'Authorization': `Bearer ${apiKey}`
    }
};

const req = https.get(url, options, (res) => {
    console.log(`状态码: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const response = JSON.parse(data);
            console.log('响应数据:', response);
            
            if (response.code === "200") {
                const now = response.now;
                console.log(`\n北京的天气:`);
                console.log(`天气状况: ${now.text}`);
                console.log(`温度: ${now.temp}°C`);
                console.log(`湿度: ${now.humidity}%`);
                console.log(`风速: ${now.windSpeed}km/h`);
                console.log(`观测时间: ${now.obsTime}`);
            } else {
                console.log(`错误: ${response.message}`);
            }
        } catch (error) {
            console.log('解析响应失败:', error);
        }
    });
});

req.on('error', (error) => {
    console.log('请求失败:', error);
});

req.end();
