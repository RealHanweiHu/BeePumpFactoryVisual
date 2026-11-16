'use strict';
(() => {
 const D = window.BEEPUMP_DATA;
 const main = document.querySelector('#main');
 if (!D) { main.textContent = '项目数据未加载。请运行 python3 scripts/project.py build-preview 后重新打开。'; return; }
 const escape = (v) => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const statusText = {complete:'已完成',blocked:'当前受阻',pending:'待执行',human_review:'人工复核节点'};
 const views=['overview','floors','templates','tasks','points'];
 let view = views.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'overview';
 let currentFloor = '8F';
 let query = '',category = 'all';
 let lastFocus;
 const navButtons=[...document.querySelectorAll('[data-view]')];
 document.querySelector('#nav-count').textContent=D.templates.length;
 const tile = t => `<article class="template-tile"><button class="template-image-button" type="button" data-template="${escape(t.code)}" aria-label="查看 ${escape(t.code)} ${escape(t.name)}"><img src="${t.svg_data_url}" alt="${escape(t.name)} V1矢量模板" loading="lazy"></button><div class="tile-top"><span class="tile-code">${escape(t.code)}</span><span class="tile-cat">${escape(t.category)}</span></div><h3>${escape(t.name)}</h3><div class="tile-size">${escape(t.w)} × ${escape(t.h)} mm · ${escape(t.revision)} / 待审</div></article>`;
 function setView(next,focus=false){
  if (!views.includes(next)) return;
  view=next;
  try{ history.replaceState(null,'','#'+view); }catch(_){ /* file:// privacy settings may restrict history */ }
  navButtons.forEach(b=>b.dataset.view===view?b.setAttribute('aria-current','page'):b.removeAttribute('aria-current'));
  render();
  if(focus){main.focus({preventScroll:true});window.scrollTo({top:0,behavior:'instant'});}
 }
 function overview(){
  const pilot=D.floors.find(f=>f.pilot);
  const shortlist=['WF-02','WF-04','WH-01','PM-01','PM-02','FL-01'];
  const six=shortlist.map(c=>D.templates.find(t=>t.code===c)).filter(Boolean);
  main.innerHTML=`<div class="hero"><section><p class="eyebrow">BEEPUMP / FACTORY VISUAL SYSTEM</p><h1>把视觉标准，<span>落到真实的工厂。</span></h1><p class="intro">从原始图纸到点位、模板与清单。先保留可追溯的设计基线，再让 Codex 分批优化；每一项制作批准，都有对应证据。</p></section><aside class="pilot-panel"><div class="pilot-label">FIRST PILOT / 首个样板</div><div class="pilot-floor"><strong>8<span>F</span></strong><div>${escape(pilot?.baseline_function)}<small>源自既有方案 · 待本次图纸与现场复核</small></div></div></aside></div>
  <div class="strip"><strong>当前边界</strong><p>已识别DWG文件头，尚未解码楼层、尺寸和设备布局。模板库展示的是V1原稿，V2与实际点位尚未生成；本工作区不是已批准的施工图。</p></div>
  <div class="stats"><div class="stat"><p class="label">SOURCE DRAWING / 原始图纸</p><div class="number">01<em>DWG</em></div><div class="hint">AC1018 · ${(D.intake.bytes/1048576).toFixed(2)} MiB · 文件头已识别</div></div><div class="stat"><p class="label">DESIGN BASELINE / 矢量模板</p><div class="number">${D.templates.length}<em>款</em></div><div class="hint">V1.0 原件只读 · 分项进入审查</div></div><div class="stat"><p class="label">SURVEY / 点位坐标</p><div class="number text-number">尚未布点</div><div class="hint">空数据库不代表现场需求为零</div></div><div class="stat"><p class="label">ENGINEERING / 工程量</p><div class="number text-number">待校核</div><div class="hint">提案数量与批准数量分别汇总</div></div></div>
  <div class="two-column"><section><div class="section-head"><h2>一个连续的设计项目</h2></div><div class="chapter-list"><button class="chapter-row" type="button" data-go="floors"><span class="num">01</span><span><strong>以图纸为底，不重新猜测厂房</strong><small>楼层身份、原始坐标、尺寸、图层及转换缺失记录。</small></span><span class="arrow">↗</span></button><button class="chapter-row" type="button" data-go="templates"><span class="num">02</span><span><strong>以模板为标准，不让每层各做一套</strong><small>黑橙品牌、白底信息、独立状态语义；Taste规则按场景适配。</small></span><span class="arrow">↗</span></button><button class="chapter-row" type="button" data-go="points"><span class="num">03</span><span><strong>以证据为门槛，不把提案当作批准</strong><small>真实点位连接材料、安装方法、版本、数量与部门复核。</small></span><span class="arrow">↗</span></button></div></section><section><div class="section-head"><h2>Codex 的第一批工作</h2></div><div class="next-work"><div><div class="workcode">P01–P04 / LOCAL EXECUTION</div><h3>图纸接入与审美审查，<br>分开推进。</h3><p>本地转换DWG；逐项审查36款模板。CAD受阻时，先推进六款V2模板的前后对照，不凭空补点。</p><div class="pills">${shortlist.map(c=>`<span class="code-tag">${c}</span>`).join('')}</div></div><button class="button" type="button" data-go="tasks" style="margin-top:24px">查看执行任务 <span>→</span></button></div></section></div>
  <div class="section-head"><h2>首批优化对象</h2><button type="button" class="text-link" data-go="templates">浏览完整模板库 →</button></div><div class="gallery">${six.map(tile).join('')}</div><p class="notice">以上均为V1参考模板，页面不将其标记为完成的V2；真实Logo、材料、位置和上限数值需按点位确认。</p>`;
 }
 function floors(){
  main.innerHTML=`<p class="eyebrow">01 / DRAWING REGISTER</p><h1>先确认空间，再确定点位。</h1><p class="intro">下面是既有方案中的楼层功能清单，不是从本次DWG识别出的楼层结果。名称、图框、比例及现场差异须逐一核对。</p><div class="floor-layout"><div class="floor-list">${D.floors.map(f=>`<button class="floor-button ${f.floor_id===currentFloor?'selected':''}" type="button" data-floor="${f.floor_id}" aria-pressed="${f.floor_id===currentFloor}"><span class="floor-number">${f.floor_id}</span><span class="floor-fn">${escape(f.baseline_function)}<small>${f.function_status==='unconfirmed'?'功能未确认':'既有方案基线 / 待图纸核对'}</small></span><span class="badge ${f.pilot?'pilot':''}">${f.pilot?'样板先行':'未解码'}</span></button>`).join('')}</div><section class="floor-detail" id="floor-detail"></section></div>`;
  floorDetail();
 }
 function floorDetail(){
  const f=D.floors.find(x=>x.floor_id===currentFloor)||D.floors[0];
  document.querySelector('#floor-detail').innerHTML=`<div class="bigfloor">${escape(f.floor_id)}</div><h2>${escape(f.baseline_function)}</h2><span class="badge">${f.pilot?'试点基线 / 等待图纸验证':'楼层基线 / 等待图纸验证'}</span><div class="empty-plan"><div class="empty-title">尚无已校核的楼层底图</div><p>不以空白示意图替代真实布局。请由Codex在本机接入CAD，确认图框与楼层对应，完成尺寸与坐标校核后再挂接底图。</p></div><dl class="meta-dl"><dt>功能来源</dt><dd>${escape(f.function_source)}</dd><dt>CAD Layout</dt><dd>${escape(f.cad_layout||'待读取')}</dd><dt>坐标单位</dt><dd>${escape(f.coordinate_unit||'待核对，不默认毫米')}</dd><dt>比例校核</dt><dd>${f.calibration.status==='verified'?'已核对':'两处不同方向的已知尺寸 / 待核对'}</dd><dt>几何与现场</dt><dd>${escape(f.geometry_status)} / ${escape(f.site_status)}</dd></dl><p class="notice">图纸和旧方案不一致时，登记差异，不自动覆盖任一方。</p>`;
 }
 function templates(){
  const cats=[...new Set(D.templates.map(t=>t.category))];
  main.innerHTML=`<p class="eyebrow">02 / TEMPLATE LIBRARY</p><h1>同一套视觉语法，36款原始模板。</h1><p class="intro">先审查，再优化。点击查看矢量原稿、初始尺寸、安装条件与内容责任；这些尺寸是模板模块，不是现场实测尺寸。</p><div class="filterbar"><label class="field" for="search">搜索 <input id="search" type="search" value="${escape(query)}" placeholder="编号、名称或英文，例如 WF-02" autocomplete="off"></label><label class="field" for="category">类别 <select id="category"><option value="all">全部类别</option>${cats.map(c=>`<option value="${escape(c)}" ${category===c?'selected':''}>${escape(c)}</option>`).join('')}</select></label><span class="results-count" id="results-count" aria-live="polite"></span></div><div id="gallery-content"></div><p class="notice">V1.0 / 原件只读。下载仅用于设计审查与深化，不构成制作批准。</p>`;
  document.querySelector('#search').addEventListener('input',e=>{query=e.target.value;gallery();});
  document.querySelector('#category').addEventListener('change',e=>{category=e.target.value;gallery();});
  gallery();
 }
 function gallery(){
  const q=query.trim().toLowerCase();
  const rows=D.templates.filter(t=>(category==='all'||t.category===category)&&`${t.code} ${t.name} ${t.en}`.toLowerCase().includes(q));
  document.querySelector('#results-count').textContent=`${rows.length} / ${D.templates.length} 款模板`;
  document.querySelector('#gallery-content').innerHTML=rows.length?`<div class="gallery">${rows.map(tile).join('')}</div>`:`<div class="empty-results"><strong>没有找到匹配模板</strong><p>请尝试编号、中文名称或切换到全部类别。</p><button class="button secondary" type="button" data-clear-search>清除筛选</button></div>`;
 }
 function tasks(){
  main.innerHTML=`<p class="eyebrow">03 / EXECUTION PLAN</p><h1>把设计拆成可验证的任务。</h1><p class="intro">这是项目启动时的任务快照，不是正在运行的后台任务。Codex每一批应更新文件、测试结果和证据，然后进入下一节点。</p><div class="strip"><strong>先做什么</strong><p>运行校验 → 在本机检查CAD工具 → 盘点图纸；同时审查V1模板并制作首批六款V2。8F真实点位依赖底图校核，其他楼层依赖样板评审。</p></div><div class="task-list">${D.tasks.map(t=>`<article class="task-row"><span class="task-id">${escape(t.id)}</span><div><h3>${escape(t.title)}</h3><p>${escape(t.acceptance)}</p><span class="dependencies">${t.depends_on.length?'前置任务：'+t.depends_on.join(' / '):'已封存原始输入，不覆盖原件'}</span></div><span class="task-status ${t.status}">${statusText[t.status]||escape(t.status)}</span></article>`).join('')}</div><p class="notice">完整启动指令位于项目根目录 <span class="path">START_CODEX.md</span>。本页面不负责远程启动Codex。</p>`;
 }
 function points(){
  const rows=D.points.points;
  main.innerHTML=`<p class="eyebrow">04 / POINTS & QUANTITIES</p><h1>一个点位，一组可追溯的依据。</h1><p class="intro">坐标来自已校核图纸；版式来自受控模板；数量来自真实点位。提案、部门复核与制作放行分别记录。</p><section class="points-panel">${rows.length?`<h2>当前登记点位</h2><div class="table-scroll"><table><thead><tr><th>点位ID</th><th>楼层</th><th>模板</th><th>状态</th><th>物理牌数</th><th>每牌面数</th></tr></thead><tbody>${rows.map(p=>`<tr><td>${escape(p.point_id)}</td><td>${escape(p.floor_id)}</td><td>${escape(p.template_code)}</td><td>${escape(p.status)}</td><td>${escape(p.quantity)}</td><td>${escape(p.faces)}</td></tr>`).join('')}</tbody></table></div>`:`<h2>尚未布点，不生成零工程量。</h2><p>本次DWG没有完成几何解码，坐标、朝向、安装高度与数量保持空缺。量表导出器会拒绝用空数据生成“全厂需要0块牌”的错误结论。</p>`}<div class="gate-steps"><div class="gate"><b>01 / GEOMETRY</b><strong>校核底图</strong><small>楼层、单位、图纸版本与两处尺寸证据。</small></div><div class="gate"><b>02 / PROPOSAL</b><strong>提出点位</strong><small>世界坐标、朝向、模板版本与放置理由。</small></div><div class="gate"><b>03 / REVIEW</b><strong>分项复核</strong><small>内容、位置、安装及相关安全事项由负责人确认。</small></div><div class="gate"><b>04 / QUANTITY</b><strong>按状态统计</strong><small>物理牌数与印刷面数分别计；不混用米、平方米。</small></div></div></section><div class="strip"><strong>数据来源</strong><p><span class="path">data/points.json</span> 是点位主数据。当前工具只汇总标牌件数；地面划线长度、涂装面积和损耗需单独按经校核的几何统计。</p></div>`;
 }
 const renderers={overview,floors,templates,tasks,points};
 function render(){renderers[view]();}
 function showTemplate(code){
  const t=D.templates.find(t=>t.code===code);if(!t)return;
  lastFocus=document.activeElement;
  const s=t.spec||{};
  document.querySelector('#dialog-code').textContent=`${t.code} / ${t.revision} / TEMPLATE ONLY`;
  const fields=[['目标',s.goal],['版式',s.layout],['材料建议',s.material],['安装与初始模块',s.mount],['责任与更新',`${s.owner||''} ${s.trigger||''}`],['验收要点',s.checks],['制作前确认',s.confirm],['来源',s.source]];
  document.querySelector('#dialog-content').innerHTML=`<div class="dialog-grid"><div><div class="dialog-image"><img src="${t.svg_data_url}" alt="${escape(t.name)}完整V1模板"></div><p class="notice">${t.w} × ${t.h} mm / 模板初始模块；请勿将显示比例作为现场尺寸。</p><a class="button secondary" href="${t.svg_data_url}" download="${escape(t.code+'_'+t.name+'_V1.0.svg')}">保存V1 SVG参考稿 ↓</a></div><div class="dialog-spec"><h2 id="dialog-title">${escape(t.name)}</h2><p class="en">${escape(t.en)}</p><div class="dialog-warning">原V1文件，尚非V2成果。用于审查和深化；最终内容、材料、位置和安全要求另行批准。</div><dl>${fields.filter(x=>x[1]).map(([k,v])=>`<dt>${k}</dt><dd>${escape(v)}</dd>`).join('')}</dl></div></div>`;
  document.querySelector('#template-dialog').showModal();
 }
 document.addEventListener('click',e=>{
  const nav=e.target.closest('[data-view]');if(nav){setView(nav.dataset.view,true);return;}
  const go=e.target.closest('[data-go]');if(go){setView(go.dataset.go,true);return;}
  const t=e.target.closest('[data-template]');if(t){showTemplate(t.dataset.template);return;}
  const f=e.target.closest('[data-floor]');if(f){currentFloor=f.dataset.floor;document.querySelectorAll('[data-floor]').forEach(b=>{b.classList.toggle('selected',b===f);b.setAttribute('aria-pressed',String(b===f));});floorDetail();return;}
  if(e.target.closest('[data-clear-search]')){query='';category='all';templates();document.querySelector('#search').focus();}
 });
 const dialog=document.querySelector('#template-dialog');
 document.querySelector('#dialog-close').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',()=>{if(lastFocus?.isConnected)lastFocus.focus();});
 dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
 window.addEventListener('hashchange',()=>{const h=location.hash.slice(1);if(views.includes(h)&&h!==view)setView(h);});
 setView(view);
})();
