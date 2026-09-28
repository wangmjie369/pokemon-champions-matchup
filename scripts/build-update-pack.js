const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const root=path.resolve(__dirname,'..');
function loadGlobal(rel){const old=global.window;global.window={};delete require.cache[require.resolve(path.join(root,rel))];require(path.join(root,rel));const value=global.window;global.window=old;return value}
const data=loadGlobal('data/champions-data.js').CHAMPIONS_DATA;
const zh=loadGlobal('data/champions-zh.js').CHAMPIONS_ZH;
const usage=loadGlobal('data/usage-mc.js').CHAMPIONS_USAGE;
const payload={data,zh,usage};
const content=JSON.stringify(payload);
const hash=crypto.createHash('sha256').update(content).digest('hex');
const version=process.env.UPDATE_VERSION||`data-${hash.slice(0,16)}`;
const generatedAt=new Date().toISOString();
const pack={version,generatedAt,regulation:'M-C',data,zh,usage};
fs.mkdirSync(path.join(root,'update'),{recursive:true});
fs.writeFileSync(path.join(root,'update','update-pack.json'),JSON.stringify(pack)+'\n');
fs.writeFileSync(path.join(root,'update','version.json'),JSON.stringify({version,generatedAt,regulation:'M-C',files:{'update-pack.json':hash}},null,2)+'\n');
fs.writeFileSync(path.join(root,'data','version.js'),`window.CHAMPIONS_LOCAL_VERSION = "${version}";\n`);
console.log(JSON.stringify({version,hash,generatedAt,dataBytes:content.length}));
