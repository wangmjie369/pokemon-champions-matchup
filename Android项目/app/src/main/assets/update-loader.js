(function(){
  const CACHE_KEY='champions-update-pack-v1';
  const cfg=window.CHAMPIONS_UPDATE_CONFIG||{};
  const localVersion=window.CHAMPIONS_LOCAL_VERSION||'0';
  const base=(cfg.baseUrl||'').replace(/\/$/,'');
  function setStatus(message,error){
    const el=document.getElementById('updateStatus');
    if(el){el.textContent=message;el.classList.toggle('error',!!error)}
    window.CHAMPIONS_UPDATE_STATUS=message;
  }
  function applyPack(pack){
    if(!pack||!pack.data||!pack.zh||!pack.usage)return false;
    window.CHAMPIONS_DATA=pack.data;
    window.CHAMPIONS_ZH=pack.zh;
    window.CHAMPIONS_USAGE=pack.usage;
    window.CHAMPIONS_VERSION=pack.version;
    return true;
  }
  try{
    const cached=JSON.parse(localStorage.getItem(CACHE_KEY)||'null');
    const current=window.CHAMPIONS_VERSION||localVersion;
    if(cached&&cached.version&&cached.version!==current)applyPack(cached);
    else window.CHAMPIONS_VERSION=current;
  }catch{window.CHAMPIONS_VERSION=window.CHAMPIONS_VERSION||localVersion}
  async function check(force){
    if(!base){setStatus('未配置在线更新源。',false);return false}
    if(location.protocol==='file:'&&base.startsWith('.')){setStatus('当前使用 APK 内置数据。',false);return false}
    const current=window.CHAMPIONS_VERSION||localVersion;
    const last=Number(localStorage.getItem('champions-update-last-check')||0);
    const interval=Math.max(1,Number(cfg.checkIntervalHours||4))*3600000;
    if(!force&&Date.now()-last<interval){setStatus('当前数据版本：'+current);return false}
    setStatus('正在检查更新...');
    try{
      const vres=await fetch(base+'/version.json?_='+Date.now(),{cache:'no-store'});
      if(!vres.ok)throw new Error('version '+vres.status);
      const manifest=await vres.json();
      localStorage.setItem('champions-update-last-check',String(Date.now()));
      if(!manifest.version||manifest.version===current){setStatus('当前数据已是最新：'+current);return false}
      const pres=await fetch(base+'/update-pack.json?_='+Date.now(),{cache:'no-store'});
      if(!pres.ok)throw new Error('pack '+pres.status);
      const pack=await pres.json();
      if(pack.version!==manifest.version)throw new Error('version mismatch');
      localStorage.setItem(CACHE_KEY,JSON.stringify(pack));
      setStatus('发现新版本 '+pack.version+'，正在刷新...');
      const reloaded=sessionStorage.getItem('champions-update-reloaded');
      if(!reloaded){sessionStorage.setItem('champions-update-reloaded','1');location.reload();return true}
      applyPack(pack);setStatus('已更新到 '+pack.version);return true;
    }catch(error){
      setStatus('检查更新失败，继续使用本地数据。',true);
      return false;
    }
  }
  window.checkChampionsUpdate=()=>check(true);
  window.CHAMPIONS_UPDATE_CHECK=check;
  window.addEventListener('DOMContentLoaded',()=>{
    const button=document.getElementById('checkUpdateBtn');
    if(button)button.addEventListener('click',()=>check(true));
    setStatus('当前数据版本：'+(window.CHAMPIONS_VERSION||localVersion));
    setTimeout(()=>check(false),1200);
  });
})();
