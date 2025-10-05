(function(){
  const W = window;
  if (W.__geminiChatWidgetInjected) return;
  W.__geminiChatWidgetInjected = true;

  const ORIGIN = (document.currentScript && document.currentScript.getAttribute('data-origin')) || (location.origin);
  const BUTTON_COLOR = '#FFA500';

  const btn = document.createElement('button');
  btn.setAttribute('aria-label','Open chat');
  Object.assign(btn.style, {
    position:'fixed', right:'20px', bottom:'20px', zIndex: 999999,
    background: BUTTON_COLOR, color:'#fff', border:'0', borderRadius:'9999px',
    width:'56px', height:'56px', boxShadow:'0 8px 24px rgba(0,0,0,0.2)', cursor:'pointer'
  });
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M2.25 12l18-9-4.5 9 4.5 9-18-9z"/></svg>';

  const panel = document.createElement('div');
  Object.assign(panel.style, {
    position:'fixed', right:'20px', bottom:'86px', width:'380px', height:'560px',
    maxWidth:'calc(100vw - 40px)', maxHeight:'calc(100vh - 140px)', background:'#fff',
    borderRadius:'16px', overflow:'hidden', boxShadow:'0 20px 60px rgba(0,0,0,0.25)',
    transition:'transform .2s ease, opacity .2s ease', transform:'translateY(8px)', opacity:'0',
    zIndex: 999998, display:'none'
  });

  const iframe = document.createElement('iframe');
  iframe.src = ORIGIN + '/embed.html';
  iframe.title = 'T.O.N.Y Chatbot';
  iframe.style.border = '0';
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  panel.appendChild(iframe);

  function open(){ panel.style.display='block'; requestAnimationFrame(()=>{ panel.style.opacity='1'; panel.style.transform='translateY(0)'; }); }
  function close(){ panel.style.opacity='0'; panel.style.transform='translateY(8px)'; setTimeout(()=>{ panel.style.display='none'; }, 180); }

  let isOpen = false;
  btn.addEventListener('click', ()=>{ isOpen ? close() : open(); isOpen = !isOpen; });

  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape' && isOpen){ close(); isOpen=false; } });

  document.body.appendChild(panel);
  document.body.appendChild(btn);
})();

