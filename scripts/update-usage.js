const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const BASE='https://www.pikalytics.com/ai/pokedex/gen9championsvgc2026regmc/';
function loadGlobal(rel){const old=global.window;global.window={};delete require.cache[require.resolve(path.join(root,rel))];require(path.join(root,rel));const value=global.window;global.window=old;return value}
const data=loadGlobal('data/champions-data.js').CHAMPIONS_DATA;
const old=loadGlobal('data/usage-mc.js').CHAMPIONS_USAGE;
const names=data.roster.map(x=>x.name).filter(n=>!n.includes('-Mega'));
const entries={};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function parseSection(md,title){const m=md.match(new RegExp('## '+title+'\\s*\\n([\\s\\S]*?)(?=\\n## |\\n---|$)','i'));return m?[...m[1].matchAll(/- \*\*(.+?)\*\*:\s*([\d.]+)%/g)].map(x=>({name:x[1],usage:+x[2]})):[]}
function candidates(name){return [...new Set([name,name.replace(/’/g,"'"),name.replace(/’/g,''),name.split('-')[0]].filter(Boolean))]}
async function fetchOne(name){for(let attempt=0;attempt<3;attempt++){for(const c of candidates(name)){try{const r=await fetch(BASE+encodeURIComponent(c),{headers:{'User-Agent':'Mozilla/5.0 champions-update-bot'}});if(!r.ok)continue;const md=await r.text();const moves=parseSection(md,'Common Moves').slice(0,4),abilities=parseSection(md,'Common Abilities');if(moves.length||abilities.length)return{moves,abilities,sourceUrl:BASE+encodeURIComponent(c)}}catch{}}await sleep(300)}return null}
let cursor=0;const worker=async()=>{while(cursor<names.length){const n=names[cursor++];const v=await fetchOne(n);if(v)entries[n]=v;await sleep(80)}};
(async()=>{await Promise.all(Array.from({length:3},worker));for(const name of data.roster.map(x=>x.name).filter(n=>n.includes('-Mega'))){const base=name.slice(0,name.indexOf('-Mega'));if(entries[base])entries[name]={moves:entries[base].moves,abilities:[],sourceUrl:entries[base].sourceUrl}}const merged={...(old&&old.entries||{}),...entries};const output={source:'Pikalytics AI Pokedex',format:'gen9championsvgc2026regmc',regulation:'M-C',fetchedAt:new Date().toISOString(),entries:merged};fs.writeFileSync(path.join(root,'data','usage-mc.js'),'window.CHAMPIONS_USAGE = '+JSON.stringify(output)+';\n');console.log(JSON.stringify({fetched:Object.keys(entries).length,total:Object.keys(merged).length}));})();
