/* Live settings implementation on the 1672 x 941 reference coordinate grid.
   Only the contextual illustration regions reuse concept artwork. */
const settingsReferenceArt={
 mouse:[1128,529,470,278], 'mouse-behavior':[1128,481,470,308],
 'keyboard-bindings':[1128,473,470,342], 'controller-layout':[1158,548,431,261],
 'controller-look':[1127,516,469,258], 'controller-deadzones':[1127,510,469,300],
 'controller-bindings':[1158,492,431,300], 'audio-volume':[1208,520,320,274],
 'audio-voice':[1208,529,320,279], 'video-display':[1134,511,466,284],
 'video-graphics':null,'access-readability':[1123,532,480,276],
 'access-comfort':[1127,512,470,270], 'gameplay-hud':[1130,552,469,228]
};
const settingsHelpCopy={
 mouse:'Controls how fast the camera rotates when you move the mouse. A higher value makes the camera turn faster.',
 'mouse-behavior':'Hold to aim, or press once to toggle.',
 'controller-layout':'Controls which button icons are shown in game. Auto detects your controller type. You can also force Xbox or PlayStation button prompts.',
 'controller-look':'Adjust camera speed when using the right stick.',
 'controller-deadzones':'Ignore small stick movements to reduce drift.',
 'audio-volume':'Gunfire, footsteps, vehicles and impacts.',
 'audio-voice':'Available when online play is enabled.',
 'video-display':'Adjust world resolution while keeping the interface sharp.',
 'video-graphics':'Balance visual detail and performance.',
 'access-readability':'Changes the size of HUD elements such as health, shields, inventory and other on-screen indicators.',
 'access-comfort':'Reduce nonessential animation and camera movement.',
 'gameplay-hud':'Sets a margin around the edge of the screen to keep important HUD elements away from the very edge. A higher value increases the inset.'
};
const settingsDefaultHelp={'audio-volume':1,'video-display':2,'gameplay-hud':4};
let settingsVisitedPage='';
function categoryReferenceFrame(selected){return '<svg class="category-reference-frame" viewBox="0 0 290 58" preserveAspectRatio="none" aria-hidden="true"><path d="M13 1H277L289 13V45L277 57H13L1 45V13Z"/>'+(selected?'<path class="category-selection-bracket" d="M24 0H12L0 12V46L12 58H24L10 44V14Z"/>':'')+'</svg>';}
function settingsBorder(){return '<svg class="settings-border" viewBox="0 0 1040 494" preserveAspectRatio="none" aria-hidden="true"><path d="M16 1H1014L1039 26V469L1014 493H25L1 469V17Z"/><path d="M16 4H1012L1035 27V467L1012 489H26L5 467V18" opacity=".3"/></svg>';}
function settingBracket(){return '<svg class="setting-bracket" viewBox="0 0 34 78" aria-hidden="true"><path fill="#c5f277" stroke="none" d="M34 0H14L0 14V64L14 78H34L11 62V16Z"/></svg>';}
function control(r,disabled=false){
 const d=disabled?' disabled':'',value=state.settings[r.id];
 const arrow=direction=>'<button class="adjust" data-adjust="'+r.id+'" data-direction="'+direction+'" aria-label="'+(direction<0?'Decrease ':'Increase ')+esc(r.label)+'"'+d+'>'+svg('<path d="'+(direction<0?'M62 20 34 50 62 80':'M38 20 66 50 38 80')+'"/>')+'</button>';
 if(r.type==='range')return arrow(-1)+'<input type="range" id="'+r.id+'" data-range="'+r.id+'" min="'+r.min+'" max="'+r.max+'" step="'+r.step+'" value="'+value+'" style="--fill:'+((value-r.min)/(r.max-r.min)*100)+'%" aria-label="'+esc(r.label)+'"'+d+'>'+arrow(1)+'<output for="'+r.id+'" class="value">'+fmt(r)+'</output>';
 if(r.id==='crosshair')return arrow(-1)+'<div class="crosshair-options">'+r.options.map(o=>'<button class="'+(value===o?'active':'')+'" data-segment="'+r.id+'" data-value="'+esc(o)+'" aria-label="'+o+' crosshair" aria-pressed="'+(value===o)+'">'+svg(o==='Dot'?'<circle cx="50" cy="50" r="5" fill="currentColor"/>':o==='Circle'?'<circle cx="50" cy="50" r="24" stroke-dasharray="25 12"/><circle cx="50" cy="50" r="3" fill="currentColor"/>':'<path d="M50 10v22m0 36v22M10 50h22m36 0h22"/>')+'</button>').join('')+'</div>'+arrow(1);
 if(r.id==='rawMouse')return '<div class="segments raw-mouse-segments">'+[false,true].map(v=>'<button class="'+(value===v?'active':'')+'" '+(value!==v?'data-toggle="'+r.id+'"':'')+' aria-pressed="'+(value===v)+'">'+(v?'On':'Off')+'</button>').join('')+'</div>';
 if(r.type==='segments'){const flank=['buttonPrompts','responseCurve'].includes(r.id);return (flank?arrow(-1):'')+'<div class="segments '+(flank?'flanked':'')+'">'+r.options.map(o=>'<button class="'+(value===o?'active':'')+'" data-segment="'+r.id+'" data-value="'+esc(o)+'" aria-pressed="'+(value===o)+'"'+d+'>'+esc(o)+'</button>').join('')+'</div>'+(flank?arrow(1):'');}
 if(r.type==='toggle')return arrow(-1)+'<button class="choice-trigger toggle '+(value?'on':'')+'" data-toggle="'+r.id+'" aria-label="'+esc(r.label)+'" aria-pressed="'+value+'"'+d+'>'+(value?'On':'Off')+'</button>'+arrow(1);
 return arrow(-1)+'<button class="choice-trigger" data-choice="'+r.id+'" aria-label="'+esc(r.label)+'" aria-haspopup="listbox" aria-expanded="false"'+d+'>'+esc(value)+'<span class="chevron">▾</span></button>'+arrow(1);
}
const settingsOriginalRebuiltScreen=settingsScreen;
settingsScreen=function(id){return settingsOriginalRebuiltScreen(id).replace(/(<button class="action category [^>]+>)([\s\S]*?)(<\/button>)/g,(all,open,inner,close)=>open+inner+categoryReferenceFrame(open.includes('selected'))+close);};
function helpContent(p,i){
 const defaultIndex=settingsDefaultHelp[p.id]||0,r=p.rows[i]||p.rows[0];
 let title=p.binding?(p.controller?'Customize bindings':'Rebind controls'):r.label;
 let copy=p.binding?(p.controller?'Select an action, then press a button.':'Select a binding to change it.'):(i===defaultIndex?settingsHelpCopy[p.id]:null)||r.help||('Adjust '+r.label.toLowerCase()+' to suit your preference.');
 let art=''; const crop=settingsReferenceArt[p.id];
 if(crop){const [x,y,w,h]=crop;art='<div class="settings-reference-diagram" role="img" aria-label="'+esc(title)+' illustration" style="left:'+(x-1100)+'px;top:'+(y-334)+'px;width:'+w+'px;height:'+h+'px;background-image:url(references/'+p.ref+');background-position:-'+x+'px -'+y+'px"></div>';}
 if(p.id==='video-graphics')art='<div class="settings-quality-table">'+[['Low','Faster performance,<br>lower visual detail.'],['Medium','Balanced performance<br>and visual quality.'],['High','Higher visual detail,<br>increased performance cost.'],['Ultra','Maximum visual detail,<br>highest performance cost.'],['Custom','Manually configured<br>settings.']].map(([n,t])=>'<div><strong>'+n+'</strong><p>'+t+'</p></div>').join('')+'</div>';
 return settingsBorder()+'<h2>'+esc(title)+'</h2><div class="help-separator"></div><p>'+esc(copy)+'</p>'+art;
}
function settingsScreen(id){
 const p=pages.find(p=>p.id===id)||pages[0];lastSettings=p.id;
 if(settingsVisitedPage!==p.id){helpIndex=settingsDefaultHelp[p.id]||0;settingsVisitedPage=p.id;}
 helpIndex=Math.min(helpIndex,p.rows.length-1);const local=pages.filter(x=>x.category===p.category);
 let rows='';
 if(p.binding){rows=(p.controller?'':'<div class="binding-head"><span>Action</span><span>Primary</span><span>Secondary</span></div>')+p.rows.map(([name,key],i)=>{const k=p.id+':'+i,val=state.bindings[k]||[key,'—'];const keycap=v=>p.controller&&['A','B','X','Y'].includes(v)?'<span class="controller-key key-'+v+'">'+v+'</span>':esc(v);return '<div class="setting-row '+(i===helpIndex?'active':'')+'" data-help="'+i+'">'+settingBracket()+'<span class="setting-label">'+name+'</span><button class="bind-button" data-bind="'+k+'" data-column="0" aria-label="Rebind '+name+'">'+keycap(val[0])+'</button>'+(p.controller?'':'<button class="bind-button" data-bind="'+k+'" data-column="1" aria-label="Secondary binding for '+name+'">'+esc(val[1])+'</button>')+'</div>';}).join('');}
 else rows=(p.disabled?'<p class="planned">PLANNED ONLINE FEATURE</p>':'')+p.rows.map((r,i)=>'<div class="setting-row '+(i===helpIndex?'active':'')+'" data-help="'+i+'">'+settingBracket()+'<label class="setting-label" '+(r.type==='range'?'for="'+r.id+'"':'')+'>'+esc(p.id==='mouse-behavior'?r.label.replace(' behavior',''):r.label)+'</label><div class="control control-'+r.type+'">'+control(r,p.disabled)+(p.disabled?'<span class="unavailable">Unavailable</span>':'')+'</div></div>').join('');
 return '<section class="screen settings-screen settings-rebuilt" data-settings-page="'+p.id+'">'+head(returnTo)+'<h1>Settings</h1><div class="categories">'+categories.map((c,i)=>'<button class="action category '+(i===p.category?'selected':'')+'" data-nav="'+pages.find(x=>x.category===i).id+'">'+icon(catIcons[i])+c+'</button>').join('')+'</div><div class="subtabs" role="tablist" aria-label="'+categories[p.category]+'">'+local.map(x=>'<button role="tab" aria-selected="'+(x.id===id)+'" class="subtab '+(x.id===id?'active':'')+'" data-nav="'+x.id+'">'+x.tab+'</button>').join('')+'</div><div class="settings-body"><div class="frame settings-rows '+(p.binding?'bindings':'')+' '+(p.controller?'controller-bindings':'')+'">'+settingsBorder()+'<div class="settings-row-scroll">'+rows+'</div></div><aside class="frame help" id="help-panel">'+helpContent(p,helpIndex)+'</aside></div>'+footer(true)+'</section>';
}
