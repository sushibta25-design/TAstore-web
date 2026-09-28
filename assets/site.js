(()=>{
'use strict';
const header=document.querySelector('.top'),toggle=document.querySelector('.menu-toggle'),nav=document.querySelector('#siteNav');
const setMenu=open=>{if(!toggle||!header)return;header.classList.toggle('menu-open',open);toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Đóng danh mục':'Mở danh mục')};
toggle?.addEventListener('click',()=>setMenu(toggle.getAttribute('aria-expanded')!=='true'));
nav?.addEventListener('click',e=>{if(e.target.closest('a'))setMenu(false)});
document.addEventListener('click',e=>{if(header&&!header.contains(e.target))setMenu(false)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle?.getAttribute('aria-expanded')==='true'){setMenu(false);toggle.focus()}});
window.matchMedia('(min-width:951px)').addEventListener('change',()=>setMenu(false));
const dialog=document.querySelector('#accountDialog');let opener=null;
document.querySelectorAll('.desktop-login,.mobile-login').forEach(button=>button.addEventListener('click',()=>{opener=button;setMenu(false);dialog?.showModal()}));
dialog?.querySelectorAll('.dialog-close,.dialog-done').forEach(b=>b.addEventListener('click',()=>dialog.close()));
dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});
dialog?.addEventListener('close',()=>{if(opener?.classList.contains('mobile-login'))toggle?.focus();else opener?.focus()});
})();