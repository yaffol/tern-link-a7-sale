(async function(){
  const listingRes = await fetch('data/listing.json', { cache: 'no-store' });
  const listing = await listingRes.json();

  document.title = listing.title || document.title;
  const price = document.getElementById('price');
  price.textContent = listing.price || '';

  // Tagline from summary (shortened) or location
  const tagline = document.querySelector('.site-header .tagline');
  if(tagline){ tagline.textContent = (listing.tagline || listing.location || ''); }

  const condition = document.getElementById('condition');
  condition.textContent = listing.condition || '';

  const specs = document.getElementById('specs');
  (listing.specs||[]).forEach(s=>{ const li=document.createElement('li'); li.textContent=s; specs.appendChild(li); });

  const extras = document.getElementById('extras');
  (listing.extras||[]).forEach(s=>{ const li=document.createElement('li'); li.textContent=s; extras.appendChild(li); });

  const availability = document.getElementById('availability');
  availability.textContent = listing.availability || '';

  const wa = listing.whatsapp||{};
  const waMsg = encodeURIComponent(wa.preferred_message||'Hi! Is this still available?');
  const waNumber = (wa.number_e164||'').replace(/[^\d+]/g,'');
  const waUrl = waNumber.startsWith('+') ? `https://wa.me/${waNumber.replace('+','')}?text=${waMsg}` : `https://wa.me/${waNumber}?text=${waMsg}`;
  const waLink = document.getElementById('whatsapp-link');
  waLink.href = waUrl;

  const coverPath = listing.cover || (listing.images&&listing.images[0]) || '';
  const cover = document.getElementById('cover');
  if(coverPath){
    cover.src = coverPath;
    cover.style.cursor = 'zoom-in';
    cover.addEventListener('click', ()=> openLightbox(coverPath));
    const base = location.origin + location.pathname.substring(0, location.pathname.lastIndexOf('/')+1);
    const abs = (p)=> base + p;
    const ogImg = document.querySelector('meta[property="og:image"]'); if (ogImg) ogImg.setAttribute('content', abs(coverPath));
    const twImg = document.querySelector('meta[name="twitter:image"]'); if (twImg) twImg.setAttribute('content', abs(coverPath));
  }
  const ogTitle = document.querySelector('meta[property="og:title"]'); if (ogTitle) ogTitle.setAttribute('content', listing.title||document.title);
  const ogDesc = document.querySelector('meta[property="og:description"]'); if (ogDesc) ogDesc.setAttribute('content', listing.summary||'');
  const ogUrl = document.querySelector('meta[property="og:url"]'); if (ogUrl) ogUrl.setAttribute('content', location.href);

  const gallery = document.getElementById('gallery');
  (listing.images||[]).forEach(src=>{
    const fig=document.createElement('figure');
    const img=document.createElement('img');
    img.loading='lazy'; img.src=src; img.alt=`${listing.model||'Tern A7'} photo`;
    img.addEventListener('click',()=>openLightbox(src));
    fig.appendChild(img); gallery.appendChild(fig);
  });

  // Album link
  const albumLink = document.getElementById('album-link');
  const albumSection = document.getElementById('album-section');
  if(listing.album_url){
    albumLink.href = listing.album_url;
  } else {
    albumSection.style.display = 'none';
  }

  // Story / narrative
  const story = document.getElementById('story');
  const storySection = document.getElementById('story-section');
  if(listing.story){ 
    story.innerHTML = listing.story.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>');
  } else { 
    storySection.style.display='none'; 
  }

  // Good / bad points
  const goodEl = document.getElementById('good-points');
  const badEl = document.getElementById('bad-points');
  const goodSection = document.getElementById('good-section');
  const badSection = document.getElementById('bad-section');
  const good = listing.good_points || [];
  const bad = listing.bad_points || [];
  if(good.length){ good.forEach(t=>{ const li=document.createElement('li'); li.textContent=t; goodEl.appendChild(li); }); } else { goodSection.style.display='none'; }
  if(bad.length){ bad.forEach(t=>{ const li=document.createElement('li'); li.textContent=t; badEl.appendChild(li); }); } else { badSection.style.display='none'; }

  const schema = {
    '@context':'https://schema.org','@type':'Product',
    name: listing.title, description: listing.summary,
    image: (listing.images||[]).map(i=>location.origin + location.pathname.substring(0, location.pathname.lastIndexOf('/')+1) + i),
    brand:{'@type':'Brand',name:'Tern'}, model: listing.model||'A7',
    offers:{'@type':'Offer',priceCurrency:'GBP',price:(listing.price||'').replace(/[^\d.]/g,''),availability:'https://schema.org/InStock',url:location.href}
  };
  document.getElementById('schema').textContent = JSON.stringify(schema);

  setupLightbox();
  function setupLightbox(){
    const lb=document.createElement('div'); 
    lb.className='lightbox'; 
    lb.innerHTML='<button class="close">×</button><button class="prev">‹</button><button class="next">›</button><img alt="full">'; 
    document.body.appendChild(lb);
    
    let currentIndex = 0;
    const allImages = listing.images || [];
    
    const close = ()=> lb.classList.remove('open');
    const showImage = (index) => {
      if(index < 0 || index >= allImages.length) return;
      currentIndex = index;
      lb.querySelector('img').src = allImages[index];
    };
    const next = () => showImage((currentIndex + 1) % allImages.length);
    const prev = () => showImage((currentIndex - 1 + allImages.length) % allImages.length);
    
    lb.querySelector('.close').addEventListener('click',close);
    lb.querySelector('.next').addEventListener('click',next);
    lb.querySelector('.prev').addEventListener('click',prev);
    lb.addEventListener('click',(e)=>{ if(e.target===lb) close(); });
    
    window.openLightbox=function(src){ 
      currentIndex = allImages.indexOf(src);
      if(currentIndex === -1) currentIndex = 0;
      showImage(currentIndex);
      lb.classList.add('open'); 
    };
    
    document.addEventListener('keydown',(e)=>{ 
      if(!lb.classList.contains('open')) return;
      if(e.key==='Escape') close();
      if(e.key==='ArrowLeft') prev();
      if(e.key==='ArrowRight') next();
    });
  }
})();
