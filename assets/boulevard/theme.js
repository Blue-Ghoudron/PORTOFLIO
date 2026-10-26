/* light/dark theme for the L'Boulevard pages: saved choice, else the system setting; runs in <head> so the page paints in the right theme */
(function(){
  var root=document.documentElement, KEY='lbv-theme';
  try{ root.dataset.theme=localStorage.getItem(KEY)||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'); }catch(e){}
  document.addEventListener('DOMContentLoaded',function(){
    var b=document.getElementById('theme'); if(!b) return;
    function label(){ var l=root.dataset.theme==='light'; b.textContent=l?'Dark':'Light'; b.setAttribute('aria-label','Switch to '+(l?'dark':'light')+' theme'); }
    b.addEventListener('click',function(){ root.dataset.theme=root.dataset.theme==='light'?'dark':'light'; try{ localStorage.setItem(KEY,root.dataset.theme); }catch(e){} label(); });
    label();
  });
})();
