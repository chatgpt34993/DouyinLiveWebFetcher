const fs = require('fs');
const vm = require('vm');

// 读取 sign.js
const signScript = fs.readFileSync('./sign.js', 'utf-8'); // 或 sign_v0.js
const context = {};
vm.createContext(context);
vm.runInContext(signScript, context);

// 生成 signature
function generateSignature(md5_param) {
    if (typeof context.get_sign === 'function') {
        return context.get_sign(md5_param);
    } else if (typeof context.getSign === 'function') {
        return context.getSign(md5_param);
    } else {
        throw new Error('sign.js 里没有 get_sign 或 getSign 方法');
    }
}

const md5_param = process.argv[2];
if (!md5_param) {
    console.error('请传入md5_param参数');
    process.exit(1);
}
const signature = generateSignature(md5_param);
console.log(signature);
