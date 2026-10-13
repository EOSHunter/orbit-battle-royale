/* Decode existing reference artwork before final QA captures; controls remain live. */
const artworkFiles=[...new Set(screens.map(s=>s.ref).filter(Boolean))];
const artworkStatus=document.createElement('span');artworkStatus.id='artwork-status';artworkStatus.textContent='Loading artwork…';artworkStatus.style.cssText='font-size:11px;color:#b4bfd0;margin-left:8px';document.querySelector('#explorer').append(artworkStatus);
const artworkImages=artworkFiles.map(file=>{const img=new Image();img.src='references/'+file;return img;});
Promise.allSettled([...artworkImages.map(img=>img.decode()),document.fonts.ready]).then(results=>{document.body.dataset.artworkReady='true';artworkStatus.textContent=results.some(r=>r.status==='rejected')?'Artwork load error':'Artwork ready';render();});
render();
