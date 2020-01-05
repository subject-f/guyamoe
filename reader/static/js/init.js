IS_MOBILE = res = (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))return true; else return false})(navigator.userAgent||navigator.vendor||window.opera);


function LoadHandler(o) {
	o=be(o);
	Linkable.call(this);

	this.parseSCP = function(url) {
		url = url.split('/');
		return {
			series: url[url.length - 3],
			chapter: url[url.length - 2].replace('-','.'),
			page: parseInt(url[url.length - 1] - 1),
		}
	}

	this.onload = () => {
	var SCP = this.parseSCP(document.location.pathname);
		API.requestSeries(SCP.series)
			.then(data => {
				Reader.setSCP(SCP);
				Reader.displaySCP(SCP);
			})
	}

	document.addEventListener("DOMContentLoaded", e => this.onload());
}

function ReaderAPI(o) {
	o=be(o);
	Linkable.call(this);

	this.url = o.url || '/api/';
	this.seriesUrl =  this.url + 'series/';
	this.mediaURL = o.mediaURL || '/media/manga/';

	this.data = {};
	this.indexData = {};

	this.infuseSeriesData = function(data) {
		for(var num in data.chapters) {
		var chapter = data.chapters[num];
			chapter.images = {};
			chapter.blurs = {};
			chapter.previews = {};
			chapter.hasWide = {};
			chapter.wides = {};

			chapter.id = num;
			for(var group in chapter.groups) {
				chapter.images[group] = [];
				chapter.blurs[group] = [];
				chapter.previews[group] = [];
				chapter.wides[group] = [];
				for (var i = 0; i < chapter.groups[group].length; i++) {
					chapter.images[group].push(
						this.mediaURL
							+ data.slug 
							+ '/chapters/' 
							+ chapter.folder 
							+ '/' 
							+ group 
							+ '/' 
							+ chapter.groups[group][i]
					)
					chapter.blurs[group].push(
						this.mediaURL
							+ data.slug 
							+ '/chapters/' 
							+ chapter.folder 
							+ '/' 
							// + "shrunk_blur_"+ group
							+ group+"_shrunk_blur" 
							+ '/' 
							+ chapter.groups[group][i]
					)
					chapter.previews[group].push(
						this.mediaURL
							+ data.slug 
							+ '/chapters/' 
							+ chapter.folder 
							+ '/' 
							// + "shrunk_"+ group
							+ group+"_shrunk" 
							+ '/' 
							+ chapter.groups[group][i]
					)
					if(chapter.groups[group][i].indexOf('_w.') > -1) {
						chapter.wides[group].push(i);
					}
				}
			}
		}
		return data;
	}

	this.requestSeries = function(slug) {
		this.seriesRequest = fetch(this.seriesUrl + slug + '/')
			.then(response => response.json())
			.then(seriesData => {
				seriesData = this.infuseSeriesData(seriesData);
				seriesData.chaptersIndex =
					Object.keys(
						seriesData.chapters
					).sort((a,b) => parseFloat(a) - parseFloat(b));
				seriesData.volMap = {};
				for (var i = 0; i < seriesData.chaptersIndex.length; i++) {
					if(!seriesData.volMap[seriesData.chapters[seriesData.chaptersIndex[i]].volume])
						seriesData.volMap[seriesData.chapters[seriesData.chaptersIndex[i]].volume] = seriesData.chaptersIndex[i];
				}
				this.data[slug] = seriesData;
				this.S.out('seriesUpdated', this.data[slug]);
			})
		return this.seriesRequest;
	}

	this.requestIndex = function(o){
		var formData = new FormData();
		formData.append("searchQuery", o.query)
		//formData.append("csrfmiddlewaretoken", CSRF_TOKEN)
		return fetch('/api/search_index/'+ o.slug + '/', {
				method: 'POST',
				body: formData
			})
			.then(response => response.json())
			.then(searchData => {
				this.S.out('indexUpdated', searchData);
				return {result:searchData, query: o.query};
			})
	}

	this.S.mapIn({
		'loadSeries': this.requestSeries,
		'loadIndex': this.requestIndex
	})
}

function SettingsHandler(){
	Linkable.call(this);

	this.all = {};

	this.all.fit = new Setting(
		'fit',
		'Page fit',
		[
			'fit_none',
			'fit_all_limit',
			'fit_width_limit',
			'fit_height_limit',
			'fit_all',
			'fit_width',
			'fit_height'
		],
		(IS_MOBILE)?'fit_all_limit':'fit_width_limit',
		{
			'fit_none': 'Images are displayed in natural resolution.',
			'fit_all_limit': 'Natural image size that does not exceed max width or height.',
			'fit_width_limit': 'Natural image size that does not exceed max width.',
			'fit_height_limit': 'Natural image size that does not exceed max height.',
			'fit_all': 'Images scale to width or height.',
			'fit_width': 'Images scale to max width.',
			'fit_height': 'Images scale to max height.',
		} 
	)
	this.all.layout = new Setting(
		'layout',
		'Reader layout',
		['ltr', 'ttb', 'rtl'],
		'ltr',
		{
			ltr: 'Layout set to left-to-right.',
			ttb: 'Layout set to top-to-bottom.',
			rtl: 'Layout set to right-to-left.'
		}
	)
	this.all.spread = new Setting(
		'spread',
		'2-page spread',
		['p1', 'p2', 'p2-odd'],
		'p1',
		{
			'p1': 'Single-page layout',
			'p2': 'Two-page layout',
			'p2-odd': 'Two-page layout, odd'
		},
		value => {
			({
				'p1': v => {
					this.set('spreadCount', 1)
					this.set('spreadOffset', 0)
				},
				'p2': v => {
					this.set('spreadCount', 2)
					this.set('spreadOffset', 0)
				},
				'p2-odd': v => {
					this.set('spreadCount', 2)
					this.set('spreadOffset', 1)
				}
			})[value]()
		}
	)
	this.all.spreadCount = new Setting(
		'spreadCount',
		'2-page spread count',
		[1, 2],
		1,
		i => {
			return 'Spread page count: %i'.replace('%i', i)
		}
	)
	this.all.spreadOffset = new Setting(
		'spreadOffset',
		'2-page spread offset',
		i => {
			return [...Array(this.all.spreadCount.get()).keys()]
			// return i >= this.all.spreadCount.get()?null:i;
		},
		0,
		i => {
			return 'Spread page offset: %i pages'
				.replace('%i', i)
				.replace('1 pages', '1 page')
				.replace('Spread page offset: 0 pages', 'No offset');
		}
	)
	this.all.groupPreference = new Setting(
		'groupPreference',
		'Group preference',
		[]
	)
	this.all.selectorPinned = new Setting(
		'selectorPinned',
		'Page selector',
		(IS_MOBILE)?['selector-fade', 'selector-pinned']:['selector-fade', 'selector-pinned', 'selector-pinned-nonum'],
		'selector-fade',
		{
			'selector-pinned': (IS_MOBILE)?'':'Page selector pinned with number.',
			'selector-pinned-nonum': 'Page selector pinned without number.',
			'selector-fade': (IS_MOBILE)?'':'Page selector is shown on hover.'
		}
	)
	this.all.preload = new Setting(
		'preload',
		'Preload amount',
		[1,2,3,4,5,6,7,8,9,100],
		(IS_MOBILE)?2:3,
		i => 'Reader will preload %i pages.'.replace('%i', i)
			.replace('1 pages', '1 page')
			.replace('100 pages', 'all pages')
	)
	this.all.sidebar = new Setting(
		'sidebar',
		'Sidebar',
		['hide', 'show'],
		'show',
		{
			'hide': '',
			'show': '',
		}
	)
	this.all.previews = new Setting(
		'previews',
		'Previews',
		['hide', 'show'],
		'hide',
		{
			'hide': '',
			'show': '',
		}
	)
	this.all.zoom = new Setting(
		'zoom',
		'Zoom level',
		['10', '20', '30', '40', '50', '60', '70', '80', '90', '100'],
		'100',
		i => 'Zoom level set to %i%.'.replace('%i', i)
	)

	this.sendInit = function() {
		for(var setting in this.all) {
			this.S.out('settingsPacket', new SettingsPacket('change', setting, this.get(setting)))
		}
	}

	this.serialize = function() {
	var settings = {};
		for(var setting in this.all) {
			settings[setting] = this.all[setting].get();
		}
		// delete groupPreference from localstorage so it does not load preferred group even on better quality release
		delete settings['groupPreference'];
		settings.VER = this.ver;
		return JSON.stringify(settings);
	}

	this.deserialize = function() {
		if(!window.localStorage) return;
	var settings = window.localStorage.getItem('settings');
		if(!settings) return;
		try{
			settings = JSON.parse(settings);
			if(settings.VER && settings.VER != this.ver) {
				throw 'Settings ver changed';
			}
			for(var setting in settings) {
				if(setting == 'VER') continue;
				this.set(setting, settings[setting], true);
			}
		}catch (e){
			localStorage.setItem('settings','');
			console.warn('Settings were found to be corrupted and so were reset.')
		}
	}

	this.query = function(qu) {
		for(var key in qu) {
		var setting = this.all[key];
			if(qu[key][0] == '!') {
				if(qu[key].substr(1) == setting.get()) return false;
			}else{
				if(qu[key] != setting.get()) return false;
			}
		}
		return true;
	}

	this.get = function(settingID){
		return this.all[settingID].get();
	}
	this.set = function(settingID, value, silent){
	var setting = this.all[settingID];
		if(setting.set(value) == false) return;
		if(setting.postUpdate) setting.postUpdate(setting.get());
		this.settingUpdated(setting, silent);
	}

	this.cycle = function(settingID, options, silent){
	var setting = this.all[settingID];
		if(setting.cycle(options) == false) return;
		if(setting.postUpdate) setting.postUpdate(setting.get());
		this.settingUpdated(setting, silent);
	}
	this.next = function(settingID, silent) {
	var setting = this.all[settingID];
		setting.next();
		if(setting.postUpdate) setting.postUpdate(setting.get());
		this.settingUpdated(setting, silent);
	}
	this.prev = function(settingID, silent) {
	var setting = this.all[settingID];
		setting.prev();
		if(setting.postUpdate) setting.postUpdate(setting.get());
		this.settingUpdated(setting, silent);
	}

	this.refreshAll = function() {
		for(var key in this.all) {
			this.all[key].refresh()
		}
	}

	this.settingUpdated = function(setting, silent) {
		this.refreshAll();
		if(window.localStorage)
			window.localStorage.setItem('settings', this.serialize())
		if(silent != true) {
			this.S.out('settingsPacket', new SettingsPacket('change', setting.name, setting.setting))
			this.S.out('message', setting.getFormatted());
		}
	}

	this.packetHandler = (packet) => {
		switch(packet.type) {
			case 'set':
				this.set(packet.setting, packet.value, packet.silent); 
				break;
			case 'cycle':
				this.cycle(packet.setting, packet.value, packet.silent);
				break;
		}
	}

	this.ver = '0.72';

	this.S.mapIn({
		settingsPacket: this.packetHandler,
		init: this.sendInit
	})

	this.deserialize();
}

function SettingsPacket(type, settingName, value, silent) {
	this.type = type;
	this.setting = settingName;
	this.value = value;
	this.silent = silent;
	return this;
}

function Setting(name, prettyName, options, dflt, strings, postUpdate) {
	this.name = name;
	this.prettyName = prettyName;
	this.default = dflt;
	this.setting = this.default;
	this.options = options;
	this.strings = strings;
	this.postUpdate = postUpdate;

	this.refresh = function() {
		if(this.options instanceof Function) {
			if(this.options() instanceof Array) {
				if(this.options().indexOf(this.get()) < 0)
					this.set(this.default);
			}else{
				if(this.options(this.get()) == null) {
					this.set(this.default);
				}
			}
		}else if(this.options instanceof Array){
			if(this.options.length > 0 && this.options.indexOf(this.get()) < 0)
				this.set(this.default);
		}else{
			// console.warn(this.name + ' has no valid options.')
		}
	}

	this.cycle = function(options) {
		if(this.options instanceof Function) {
			if(!(options = this.options()) instanceof Array) {
				console.log('Option', this, 'did not return an array to cycle on.')
				return false;
			}
		}else if(!(options = this.options) instanceof Array) {
			console.log('Option', this, 'was not an array nor a function.')
			return false;
		}
		if(options) {
		var index = options.indexOf(this.setting);
			return this.set(
				(index+1 > options.length - 1)?options[0]:options[index+1]
			);
		}
		return false;
	}
	this.next = function() {
		if(this.options.indexOf(this.setting) < this.options.length - 1) {
			this.set(this.options[this.options.indexOf(this.setting) + 1])
		}
	}
	this.prev = function() {
		if(this.options.indexOf(this.setting) > 0) {
			this.set(this.options[this.options.indexOf(this.setting) - 1])
		}
	}
	this.get = function() {
		return this.setting;
	}
	this.getFormatted = function() {
		if(this.strings) {
			if(this.strings instanceof Function) {
				return this.strings(this.setting);
			}
			return this.strings[this.setting];
		}else{
			return '';
		}
	}
	this.set = function(value) {
		if(value == this.setting) return false;
		if(this.options instanceof Function) {
			if(this.options() instanceof Array) {
				if(this.options().indexOf(value) < 0)
					throw new Error(this.name + ' must be one of: ' + this.options().join(', '))
			}else{
				if(this.options(value) == null) {
					throw new Error(this.name + ' did not satisfy option constraints.');
				}
			}
		}else if(this.options instanceof Array){
			if(this.options.length > 0 && this.options.indexOf(value) < 0)
				throw new Error(this.name + ' must be one of: ' + this.options.join(', '))
		}else{
			throw new Error(this.name + ' has no valid options.')
		}
		this.setting = value;
	}
}

function UI_Tooltippy(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Tooltippy'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	
	this.attached = false;

	this.handler = e => {
	var tip = e.target.getAttribute('data-tip');
		if(tip) {
			this.attached = true;
		var rect = e.target.getBoundingClientRect()
		var bodyRect = document.body.getBoundingClientRect();
		var align = e.target.getAttribute('data-tip-align')
			this.set(tip);
			this.$.style.display = 'block';
			if(IS_MOBILE) return;
			if(align == 'right')
				this.$.style.bottom = document.body.offsetHeight - (rect.top - bodyRect.top) - rect.height + this.$.offsetHeight + 2 + 'px';
			else
				this.$.style.bottom = document.body.offsetHeight - (rect.top - bodyRect.top) + 2 + 'px';
			if(e.pageX > window.innerWidth / 2) {
				this.$.style.left = 'unset';
				this.$.style.right = window.innerWidth - rect.left - rect.width + 'px';
			}else{
				this.$.style.right = 'unset';
				if(align == 'right')
					this.$.style.left = rect.left + rect.width + 4 + 'px';
				else
					this.$.style.left = rect.left + 'px';
			}
		}
	}

	this.set = function(text) {
		if(text.length < 1) return;
		text = text.replace(/\[(.|Ctrl|Shift|Meta|Alt)\]/g, '<span class="Tooltippy-key">$1</span>')
		this.$.innerHTML = text;
		if(!this.attached || IS_MOBILE) {
			this.$.style.display = 'block';
			if(IS_MOBILE) {
				this.$.style.bottom = window.innerHeight * 0.20 + 'px';
			}else{
				this.$.style.bottom = window.innerHeight * 0.90 + 'px';
			}
			this.$.style.left = 'unset';
			this.$.style.right = Reader.imageView.$.offsetWidth / 2 - this.$.offsetWidth / 2 + 'px'; // TODO: REMOVE HARDCODE
		}
		this.$.classList.remove('fadeOut');
		clearTimeout(this.fader);
		this.fader = setTimeout(() => this.$.classList.add('fadeOut'), 3000);

	}

	this.reset = function (e) { 
		this.attached = false;
		this.$.style.display = 'none';
	}

	this.attach = function(element, text, align) {
		element.onmouseover = e => this.handler(e);
		element.onmouseleave = e => this.reset(e)
		element.setAttribute('data-tip', text);
		if(align) element.setAttribute('data-tip-align', align);
		return this;
	}
}

function UI_Reader(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Reader'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this);

	this.SCP = {
		chapter: 1,
		page: 0,
	};
	
	// new KeyListener()
	// 	.condition(() => Loda.$.classList.contains('hidden'))
	// 	.condition(() => Settings.all.layout.get() != 'ttb')
	// 	.pre(() => this._.image_viewer.querySelector('.is-active').focus())

	// new KeyListener()
	// 	.condition(() => Loda.$.classList.contains('hidden'))
	// 	.condition(() => Settings.all.layout.get() == 'ttb')
	// 	.pre(() => this._.image_container.focus())
	

	new KeyListener(document.body)
		.attach('prevCh', ['BracketLeft'], e => this.prevChapter())
		.attach('nextCh', ['BracketRight'], e => this.nextChapter())
		.attach('prevVo', ['Comma'], e => this.prevVolume())
		.attach('nextVo', ['Period'], e => this.nextVolume())
		.attach('fit', ['KeyF'], e => Settings.cycle('fit'))
		.attach('layout', ['KeyD'], e => Settings.cycle('layout'))
		.attach('opacity', ['KeyO'], e => this.imageView.$.children[0].style.opacity = '0.03')
		.attach('sidebar', ['KeyS'], s => Settings.cycle('sidebar'))
		.attach('pageSelector', ['KeyN'], s => Settings.cycle('selectorPinned'))
		.attach('preload', ['KeyL'], s => Settings.cycle('preload'))
		.attach('previews', ['KeyP'], s => Settings.cycle('previews'))
		.attach('spread', ['KeyQ'], s => Settings.cycle('spread'))
		.attach('spreadCount', ['Digit1'], s => Settings.cycle('spreadCount'))
		.attach('spreadOffset', ['Digit2'], s => Settings.cycle('spreadOffset'))
		.attach('comments', ['KeyC'], s => this.openComments())
		.attach('share', ['KeyR'], s => {
			this.copyShortLink(s);
		})
		.attach('minus', ['Minus'], s => {
			Settings.set('fit', 'fit_width')
			Settings.all.zoom.prev()
		})
		.attach('plus', ['Equal'], s => {
			Settings.set('fit', 'fit_width')
			Settings.all.zoom.next()
		})

	new KeyListener(document.body)
		.attach('search', ['Ctrl+KeyF'], s => {
			Loda.display('search')
		})
		

	new KeyListener(document.body)
		.condition(() => Settings.all.layout.get() == 'ltr')
		.attach('prev', ['ArrowLeft'], e => this.prevPage())
		.attach('next', ['ArrowRight'], e => this.nextPage());

	new KeyListener(document.body)
		.condition(() => Settings.all.layout.get() == 'rtl')
		.attach('prev', ['ArrowRight'], e => this.prevPage())
		.attach('next', ['ArrowLeft'], e => this.nextPage());


	this.selector_chap = new UI_FauxDrop({
		node: this._.selector_chap
	})
	this.selector_chap.S.linkAnonymous('value', value => {
		this.drawChapter(value, 0);
	});

	this.selector_vol = new UI_FauxDrop({
		node: this._.selector_vol
	})
	this.selector_vol.S.linkAnonymous('value', value => this.selectVolume(value));

	this.imageView = new UI_ReaderImageView({
		node: this._.image_viewer
	}).S.link(this);

	this.groupList = new UI_Tabs({
		node: this._.groups
	}).S.linkAnonymous('id', id => this.drawGroup(id));

	this.selector_page = new UI_PageSelector({
		node: this._.page_selector
	})
	this.selector_page.S.linkAnonymous('page', id => this.displayPage(id));

	this.messageBox = new UI_MessageBox({
		node: this._.message
	})
	this.previews = new UI_Tabs({
		node: this._.previews
	}).S.linkAnonymous('number', id => this.displayPage(id));

	this.asideViews = new UI_WindowedContainerList({
		node: this._.aside_views,
		dynamicHide: true
	})
	//views: fit
	this.fitView = new UI_ButtonGroup({
		node: this._.aside_views_fit,
		linkedSetting: 'fit'
	}).refresh().S.biLink(Settings);

	this.updateData = function(data) {
		this.current = data;
	}

	this.setSCP = function(SCP) {
		if(SCP.series) this.SCP.series = SCP.series;
		if(SCP.chapter) this.SCP.chapter = SCP.chapter;
		if(SCP.page) this.SCP.page = SCP.page;
	}
	this.displaySCP = function(SCP) {
		this.drawReader(SCP.series);
		this.drawChapter(SCP.chapter, SCP.page);
		this.S.out('init');
	}

	this.drawReader = function(slug) {
		if(slug) this.SCP.series = slug;
		this.SCP.lastChapter = this.current.chaptersIndex[this.current.chaptersIndex.length - 1];
		this.SCP.firstChapter = this.current.chaptersIndex[0];
		this._.title.innerHTML = this.current.title;
	var chapterElements = [];
	var volElements = {};
		for (var i = this.current.chaptersIndex.length - 1; i >= 0; i--) {
		var chapterNumber = this.current.chaptersIndex[i];
		var chapter = this.current.chapters[chapterNumber];
			chapterElements.push({
				text: chapterNumber + ' - ' + chapter.title,
				value: chapterNumber
			});

		}
		volElements = Object.keys(this.current.volMap).sort((a,b) => parseFloat(b) - parseFloat(a)).map(item => {
			return {
				value: item,
			}
		});

		this.selector_chap.clear().add(chapterElements);
		this.selector_vol.clear().add(volElements);

		setTimeout(() => {
			this._.page_selector.classList.remove('vis')
			this._.zoom_level.classList.remove('vis')
		}, 3000);
		this._.close.href = '/read/manga/' + this.SCP.series;
	
	}

	this.drawGroup = function(group) {
		Settings.set('groupPreference', group);	
		this.drawChapter();
	}

	this.drawChapter = function(chapter, page) {
		if(chapter) this.SCP.chapter = chapter;
	var chapterObj = this.current.chapters[this.SCP.chapter];
		this.SCP.volume = chapterObj.volume;
		this.SCP.chapterName = chapterObj.title
	var group = Settings.all.groupPreference.get();
		if(group === undefined || chapterObj.groups[group] == undefined) {
			if(this.current.preferred_sort && chapterObj.groups[this.current.preferred_sort[0]] != undefined){
				group = this.current.preferred_sort[0]
			}else{
				group = Object.keys(chapterObj.groups)[0];
			}
		}
		this.SCP.group = group;
		this.SCP.pageCount = chapterObj.groups[group].length;
		this.SCP.lastPage = this.SCP.pageCount - 1;

		this.shuffleRandomChapter();

		this.groupList.clear();
	var groupElements = {};
		for(var grp in chapterObj.groups) {
			groupElements[grp] = new UI_SimpleListItem({
				html: '<div' + ((grp==group)?' class="is-active"':'') + '></div>',
				text: this.current.groups[grp]
			})
		}
		this.groupList.addMapped(groupElements);

		this.imageView.drawImages(chapterObj.images[group], chapterObj.wides[group]);
		if(Settings.get('previews') == 'show') this.drawPreviews();
		this.selector_chap.set(this.SCP.chapter, true);
		this.selector_vol.set(chapterObj.volume, true);

		if(this.SCP.chapter == this.SCP.lastChapter) {
			this._.chap_next.classList.add('disabled');
		}else{
			this._.chap_next.classList.remove('disabled');
		}
		if(this.SCP.chapter == this.SCP.firstChapter) {
			this._.chap_prev.classList.add('disabled');
		}else{
			this._.chap_prev.classList.remove('disabled');
		}
		if(this.SCP.volume >= Math.max.apply(null, Object.keys(this.current.volMap))) {
			this._.vol_next.classList.add('disabled');
		}else{
			this._.vol_next.classList.remove('disabled');
		}
		if(this.SCP.volume <= Math.min.apply(null, Object.keys(this.current.volMap))) {
			this._.vol_prev.classList.add('disabled');
		}else{
			this._.vol_prev.classList.remove('disabled');
		}

		this._.page_selector.classList.add('vis')
		setTimeout(() => this._.page_selector.classList.remove('vis'), 3000);

		this._.preload_entity.innerHTML = '';
		this.selector_page.clearPreload();
		this.displayPage(page);
		this._.comment_button.href = '/reader/series/' + this.SCP.series + '/' + this.SCP.chapter + '/comments'
		this.plusOne();
		return this;
	}

	this.displayPage = function(page, dry) {
		if(page == 'last')
			this.SCP.page = this.SCP.lastPage;
		else
			if(page !== undefined) this.SCP.page = page;
		
		this.SCP.page = this.imageView.imageWrappersMask[this.imageView.imageWrappersMap[this.SCP.page]][0]

		this.imageView.selectPage(this.SCP.page, dry);
		this.SCP.visiblePages = this.imageView.visiblePages;
		//this.messageBox.displayMessage(this.SCP.page + 1 + '/' + (this.current.chapters[this.SCP.chapter].images[this.SCP.group].length), 'none', 1000000)
		this.S.out('SCP', this.SCP);
	}

	this.showPreviews = function(state) {
		if(state == 'show') {
			this.$.classList.add('previews-open');
			this.drawPreviews();
		}else{
			this.$.classList.remove('previews-open')
		}

	}

	this.drawPreviews = function() {
		this.previews.clear();
		this.current.chapters[this.SCP.chapter].previews[this.SCP.group].forEach(
			preview => {
				this.previews.add(new UI_Dummy({
					html: "<img src='"+preview+"' />"
				}))
			}
		)
		this.previews.select(this.SCP.page, undefined, undefined, true);
	}

	this.selectVolume = function(vol) {
		if(this.current.volMap[vol])
			this.drawChapter(this.current.volMap[vol]);
	}

	this.plusOne = function() {
		clearTimeout(this.plusOneTimer);
		this.plusOneTimer = setTimeout(i => {
		var formData = new FormData();
			formData.append("series", this.SCP.series)
			formData.append("group", this.SCP.group)
			formData.append("chapter", this.SCP.chapter)
			fetch('/reader/update_view_count/', {
				method: 'POST',
				body: formData
			})
		}, 20*1000)
	}


	this.nextChapter = function(){
		if(this.SCP.chapter != this.SCP.lastChapter) {
		var index = this.current.chaptersIndex.indexOf(''+this.SCP.chapter);
			if(index < 0) throw new Error('Chapter advance failed: invalid base index.')
			this.drawChapter(
				this.current.chaptersIndex[index + 1],
				0
			)
		}
	}
	this.prevChapter = function(page) {
		if(this.SCP.chapter != this.SCP.firstChapter) {
		var index = this.current.chaptersIndex.indexOf(''+this.SCP.chapter);
			if(index < 0) throw new Error('Chapter stepback failed: invalid base index.')
			this.drawChapter(
				this.current.chaptersIndex[index - 1],
				page || 0
			)
		}
	}

	this.nextPage = function() {
	var nextWrapper = this.imageView.imageWrappersMap[this.SCP.page] + 1;
		if(nextWrapper >= this.imageView.imageWrappersMask.length) {
			this.nextChapter();
		} else {
			this.displayPage(this.imageView.imageWrappersMask[nextWrapper][0])
		}
	}

	this.prevPage = function(){
		if(this.SCP.page > 0) 
			this.displayPage(this.SCP.page - 1)
		else {
			this.prevChapter('last');
		}
	}
	this.nextVolume = function(){
		this.selectVolume(+this.SCP.volume+1);
	}
	this.prevVolume = function(){
		this.selectVolume(+this.SCP.volume-1)
	}

	this.copyShortLink = function() {
	var url = document.location.origin + '/' + this.SCP.chapter.replace('.', '-') + '/'+ (this.SCP.page+1);
		navigator.clipboard.writeText(url)
		.then(function() {
		  Tooltippy.set('Link copied to clipboard!');
		}, function(err) {
		  Tooltippy.set('Link copy failed ('+url+')');
		});
	}

	this.openComments = function() {
		if(this.SCP.series && this.SCP.chapter !== undefined)
			window.location.href = '/read/manga/' + this.SCP.series + '/' + this.SCP.chapter + '/comments';
	}

	this.setFit = function(fit) {
		Settings.all.fit.options.forEach(item => {
			this.$.classList.remove(item);
			this._.fit_button.classList.remove(item);
		});
		this.$.classList.add(fit);
		this._.fit_button.classList.add(fit);
		this.imageView.updateWides();
	}

	this.setLayout = function(layout, silent) {
		Settings.all.layout.options.forEach(item => {
			this.$.classList.remove(item);
		});
		this.$.classList.add(layout);
		this.stickHeader();

		if(!silent) {
			this.imageView.drawImages(this.current.chapters[this.SCP.chapter].images[this.SCP.group], this.current.chapters[this.SCP.chapter].wides[this.SCP.group]);
			this.imageView.selectPage(this.SCP.page);
		}
	}

	this.setSelectorPin = function(state) {
		Settings.all.selectorPinned.options.forEach(item => {
			this.$.classList.remove(item);
			this.$.classList.remove('nonum');
		});
		if(state == 'selector-pinned-nonum') {
			this.$.classList.add('selector-pinned');
			this.$.classList.add('nonum');
		}else{
			this.$.classList.add(state);
		}
		this.stickHeader();
	}

	this.setPreload = function(number){
		this.$.setAttribute('data-preload', number);
	}

	this.setZoom = function(zoom) {
		Settings.all.zoom.options.forEach(item => {
			this.$.classList.remove('zl'+item);
		});
		this.$.classList.add('zl'+zoom);
		this.imageView.updateWides();
	}
	this.setSpread = function(spread) {
		Settings.all.spread.options.forEach(item => {
			this.$.classList.remove(item);
		});
		this.$.classList.add(spread);
	}

	this.setSidebar = function(state) {
		if(state == 'hide') {
			this.$.classList.add('sidebar-hidden');
		}else{
			this.$.classList.remove('sidebar-hidden');
		}
		this.imageView.updateWides();
	}

	this.stickHeader = () => {
		if(IS_MOBILE) {
			if(this._.rdr_aside_content.offsetTop <= window.scrollY && Settings.get('layout') == 'ttb' && Settings.get('selectorPinned') == 'selector-pinned') {
				this.$.classList.add('stick');
				this._.rdr_aside_content.style.paddingTop = this._.rdr_selector.offsetHeight + 'px';
			}else{
				this.$.classList.remove('stick');
				this._.rdr_aside_content.style.paddingTop = '0px';
			}
		}
	}

	this.enqueuePreload = url => {
	var newPreload = 'url("'+url+'")';
	this._.preload_entity.style.background = newPreload;
	// var preloads = this._.preload_entity.children.map(item => item.style.background);
	// 	if(preloads.indexOf(newPreload) < 0) {
	// 	var newElement = document.createElement('div');
	// 		newElement.style.background = newPreload;
	// 		this._.preload_entity.appendChild(newElement);
	//	}
	}

	this.eventRouter = function(event){
		({
			'nextPage': () => this.nextPage(),
			'prevPage': () => this.prevPage()
		})[event.type](event.data)
	}

	this.settingsRouter = function(o) {
		if(o.type != 'change') return;
		({
			'fit': o => this.setFit(o),
			'layout': o => this.setLayout(o),
			'groupPreference': o => {},
			'selectorPinned': o => this.setSelectorPin(o),
			'preload': o => this.setPreload(o),
			'sidebar': o => this.setSidebar(o),
			'previews': o => this.showPreviews(o),
			'zoom': o => this.setZoom(o),
			'spread': o => this.setSpread(o),
			'spreadCount': o => this.drawChapter(),
			'spreadOffset': o => this.drawChapter(),
		})[o.setting](o.value)
	}

	this.shuffleRandomChapter = function() {
		if(this.SCP.chapter == '46.5' && this.SCP.series == 'Kaguya-Wants-To-Be-Confessed-To') {
			this._.random_chapter.classList.remove('is-hidden');
		} else {
			this._.random_chapter.classList.add('is-hidden');
			return;
		}

		if(!this.current.chapters[this.SCP.chapter].previewsBackup)
			this.current.chapters[this.SCP.chapter].previewsBackup = this.current.chapters[this.SCP.chapter].previews[this.SCP.group].slice();
		var previews = this.current.chapters[this.SCP.chapter].previewsBackup;
		var pages = this.current.chapters[this.SCP.chapter].images[this.SCP.group];
		function shuffle(array) {
			var currentIndex = array.length, temporaryValue, randomIndex;
			while (0 !== currentIndex) {
				randomIndex = Math.floor(Math.random() * currentIndex);
				currentIndex -= 1;
				temporaryValue = array[currentIndex];
				array[currentIndex] = array[randomIndex];
				array[randomIndex] = temporaryValue;
			}
			return array;
		}
	var subarr = previews.slice(4,16);
		subarr.unshift(subarr.pop());
	var uarr = [];
		for(var i=0; i<subarr.length; i=i+2) {
			uarr.push([subarr[i], subarr[i+1]])
			shuffle(uarr[uarr.length-1]);
		}
		uarr = shuffle(uarr);
		uarr = uarr.reduce((acc, val) => acc.concat(val), []);

		this.current.chapters[this.SCP.chapter].previews[this.SCP.group] = previews.slice(0, 4).concat(uarr,previews.slice(-1));
		this.current.chapters[this.SCP.chapter].images[this.SCP.group] = this.current.chapters[this.SCP.chapter].previews[this.SCP.group].map(p => p.replace('_shrunk',''))
	}

	this._.chap_prev.onmousedown = e => this.prevChapter();
	this._.chap_next.onmousedown = e => this.nextChapter();
	this._.vol_prev.onmousedown = e => this.prevVolume();
	this._.vol_next.onmousedown = e => this.nextVolume();
	this._.preload_button.onmousedown = e => Settings.cycle('preload');
	this._.layout_button.onmousedown = e => Settings.cycle('layout');
	this._.fit_button.onmousedown = e => {
		this.asideViews.S.call('number', 0);
	}
	this._.sel_pin_button.onmousedown = e => Settings.cycle('selectorPinned');
	this._.sidebar_button.onmousedown = e => Settings.cycle('sidebar');
	this._.previews_button.onmousedown = e => Settings.cycle('previews');
	this._.zoom_level_plus.onmousedown = e => Settings.next('zoom');
	this._.zoom_level_minus.onmousedown = e => Settings.prev('zoom');
	this._.spread_button.onmousedown = e => Settings.cycle('spread');
	this._.share_button.onmousedown = e => this.copyShortLink(e);
	this._.search.onclick = e => Loda.display('search');
	this._.random_chapter_button.addEventListener('mousedown', e => {
		e.preventDefault();
		e.stopPropagation();
		this.drawChapter(this.SCP.chapter, 2)
		return false;
	}, false)


	Tooltippy
		.attach(this._.chap_prev, 'Previous chapter [[]')
		.attach(this._.chap_next, 'Next chapter []]')
		.attach(this._.vol_prev, 'Previous volume [,]')
		.attach(this._.vol_next, 'Next volume [.]')
		.attach(this._.preload_button, 'Change preload [L]')
		.attach(this._.layout_button, 'Change layout direction [D]')
		.attach(this._.fit_button, 'Change fit mode [F]')
		.attach(this._.sel_pin_button, 'Pin page selector [N]')
		.attach(this._.sidebar_button, 'Show/hide sidebar [S]', 'right')
		.attach(this._.previews_button.querySelector('.expander'), 'Show previews [P]')
		.attach(this._.comment_button, 'Go to comments [C]')
		.attach(this._.share_button, 'Copy short link [R]')
		.attach(this._.search, 'Open search window [Ctrl]+[F]')
		.attach(this._.spread_button, 'Change page spread type [Q]')
		.attach(this._.fit_none, 'Images are displayed in natural resolution.')
		.attach(this._.fit_all, 'Images scale to width or height.')
		.attach(this._.fit_width, 'Images scale to max width.')
		.attach(this._.fit_height, 'Images scale to max height.')
		.attach(this._.fit_all_limit, 'Natural image size that does not exceed max width or height.')
		.attach(this._.fit_width_limit, 'Natural image size that does not exceed max width.')
		.attach(this._.fit_height_limit, 'Natural image size that does not exceed max height.')
		// .attach(this._.zoom_level_plus, 'Increase zoom level')
		// .attach(this._.zoom_level_minus, 'Decrease zoom level')


	this.S.mapIn({
		seriesUpdated: this.updateData,
		event: this.eventRouter,
		settingsPacket: this.settingsRouter,
		message: message => {
			Tooltippy.set(message);
		},
	})

	this.S.link(this.selector_page);
	this.S.linkAnonymous('SCP', SCP => this.previews.select(SCP.page, undefined, undefined, true));
}

function UI_ReaderImageView(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['ReaderImageView'].concat(o.kind || []),
	});
	Linkable.call(this);
	this.firstDraw = true;
	this.imageContainer = new UI_Tabs({node: this._.image_container})


	this.updateWides = () => {
		if(!this.imageWrappers) return;
		for(var i=0; i < this.imageWrappers.length; i++) {
			if(this.imageWrappers[i].$.scrollWidth > this.imageWrappers[i].$.clientWidth) {
				this.imageWrappers[i].$.classList.add('too-wide');
			}else{
				this.imageWrappers[i].$.classList.remove('too-wide');
			}
		}
	}

	new ResizeSensor(this.$, this.updateWides);

	this.drawImages = function(images, wides) {
		this.imageContainer.$.style.transition = '';
		this.imageContainer.clear();
		this.imageWrappers = [];
		this.imageWrappersMask = [];
		this.imageWrappersMap = {};
	var spreadCount = Settings.all.spreadCount.get();
	var	spreadOffset = Settings.all.spreadOffset.get();
	var imageIndices = [];
		for(var i=0; i < images.length; i++) {
			imageIndices.push(i);
			this.imageWrappersMap[i] = this.imageWrappersMask.length;
			if(wides.indexOf(i) > -1 || wides.indexOf(i+1) > -1){
				spreadOffset++;

			}
			if(spreadOffset >= spreadCount - 1 || i >= images.length - 1) {
				if(wides.indexOf(i) > -1)
					spreadOffset = Settings.all.spreadOffset.get();
				else
					spreadOffset = 0;
				this.imageWrappersMask.push(imageIndices);
				imageIndices = [];
			}else{
				spreadOffset++;
			}
		}

		this.imageWrappers = this.imageWrappersMask.map(wrapper => 
			new UI_ReaderImageWrapper({
				imageObjects: wrapper.map(index => ({
					url: images[index],
					index: index,
				}))
			})
		);

		this.imageList = [];

		this.imageWrappers.forEach(wrapper => {
			wrapper.S.link(Reader.selector_page);
			this.imageList = this.imageList.concat(wrapper.get());
		})
		if(Settings.all.layout.get() == 'rtl') {
			this.imageWrappers.reverse();
			this.imageWrappers.forEach(i => i.reverse());
		}
		this.imageContainer.add(this.imageWrappers);

		this.imageContainer.$.scroll(0,0);

		if(Settings.all.layout.get() == 'ttb') {
		var butt = new UI_Dummy();
			butt.$.classList.add('nextCha');
			butt.$.onmousedown = e => {
				e.preventDefault();
				Reader.nextChapter(0);
				document.documentElement.scrollTo({top: 0})
			}
			this.imageContainer.add(butt);
		}
	}

	this.selectPage = function(index, dry) {
		if(index < 0 || index >= this.imageList.length)
			return;

		this.selectedPage = this.imageList[index];
		this.selectedWrapper = this.selectedPage.parentWrapper;
		this.visiblePages = this.selectedWrapper.getIndices();

	var toPreload = Settings.all.preload.get();
		if(toPreload == 100) {
			toPreload = this.imageList.length - 1;
		}
		toPreload = toPreload * Settings.get('spreadCount');
		for (var i = index - 1; i < index + Math.max(toPreload, Settings.get('spreadCount')); i++) {
			if(this.imageList[i]) {
				this.imageList[i].load();
			//	Reader.enqueuePreload(this.imageList[i].url);
			}
		}
		if(this.imageList[index+1]) {
			Reader.enqueuePreload(this.imageList[index+1].url);
		}

		if(Settings.all.layout.get() != 'ttb') {
			this.imageContainer.$._translateX = ( -100 * this.imageWrappers.indexOf(this.selectedWrapper))
			this.imageContainer.$.style.transform =
				'translate3d(' + this.imageContainer.$._translateX + '%,0,0)';
		}else if (!dry){
			if(IS_MOBILE)
				window.scroll(0,this.imageList[index].$.getBoundingClientRect().top + window.scrollY);
			else
				this.imageContainer.$.scroll(0,this.imageList[index].$.parentNode.offsetTop);
		}
	}

	this.prev = function() {
		this.S.out('event', {type: 'prevPage'});

	}
	this.next = function() {
		this.S.out('event', {type: 'nextPage'})
	}

	document.onscroll = this._.image_container.onscroll = e => {
		if(this.scrollPreventer) return;
		if(Settings.all.layout.get() == 'ttb') {
			Reader.stickHeader();
		var scrollTop = (e.target.scrollingElement)?
					e.target.scrollingElement.scrollTop:
					undefined
				|| e.target.scrollTop;
		var st = scrollTop
				+ document.documentElement.clientHeight / 8 * 6
				* (scrollTop / this.imageContainer.$.scrollHeight)
				+ document.documentElement.clientHeight / 8;
		//document.getElementById('scan_line').style.bottom = (this.imageContainer.$.scrollHeight - st)/this.imageContainer.$.scrollHeight*100 +'%';
		var offsets = this.imageList.map(item => item.$.offsetTop + item.$.parentNode.offsetTop);
			offsets.push(st);
			offsets = offsets.sort((a, b) => a - b);
		var index = offsets.indexOf(st) - 1;
			if(index + 1 == offsets.length) return;
			if(Reader.SCP.page == index) return;
			for(var i=0; i<index; i++) {
				this.imageList[i].load();
			}
			Reader.displayPage(index, true);
			return;
		}else{
			// if(this.selectedWrapper.$.nextSibling)
			// 	this.selectedWrapper.$.nextSibling.style.top = this.$.scrollTop + 'px';
			// if(this.selectedWrapper.$.prevSibling)
			// 	this.selectedWrapper.$.prevSibling.style.top = this.$.scrollTop + 'px';
		}
	}

const SCROLL = 1;
const SWIPE = 2;
const SCROLL_X = 3;

	this.touch = {
		start: 0,
		startY: 0,
		initialX: 0,
		scrollY: 0,
		transitionTimer: null,
		delta: 0,
		deltaY: 0,
		em: parseFloat(getComputedStyle(document.body).fontSize),
		gesture: null,
		time: null,
		escapeVelocity: 0.1,
		escapeDelta: 40,
		imagePosition: 0,
		a: null
	};
	
	this._.image_container.ontouchstart = e => {
		if(Settings.all.layout.get() == 'ttb') return;
		if(e.touches.length > 1) return;
		this.touch.initialX = this._.image_container._translateX;
		this.touch.start = e.touches[0].pageX / this._.image_container.offsetWidth * 100;
		this.touch.startY = e.touches[0].pageY;
		this._.image_container.style.transition = '';
		this.touch.gesture = null;
		this.touch.delta = 0;
		this.touch.deltaY = 0;
		this.touch.scrollY = window.scrollY;
		this.touch.time = Date.now();
	var maxScroll = this.selectedWrapper.get().map(img => img.$.offsetWidth).reduce((i, k) => i + k) - this.selectedWrapper.$.offsetWidth;
		if(maxScroll <= 0){
			this.touch.imagePosition = null;
		}else if(Math.abs(this.selectedWrapper.$.scrollLeft) >= maxScroll-2) {
			this.touch.imagePosition = 1;
		}else if(Math.abs(this.selectedWrapper.$.scrollLeft) == 0) {
			this.touch.imagePosition = -1;
		}else{
			this.touch.imagePosition = 0;
		}
		this.touch.pageX = e.touches[0].pageX;
		this.touch.pageY = e.touches[0].pageY;
		this.touch.a = requestAnimationFrame(this.touch.anim);
	}
	
	this.touch.anim = () => {
		this.touch.a = requestAnimationFrame(this.touch.anim);
		if(this.touch.gesture == SCROLL) return cancelAnimationFrame(this.touch.a);
		if(Settings.all.layout.get() == 'ttb') return cancelAnimationFrame(this.touch.a);
		this.touch.delta = this.touch.pageX / this._.image_container.offsetWidth * 100 - this.touch.start;
		if(this.touch.imagePosition == 0
		|| this.touch.imagePosition == 1 && this.touch.delta > 0
		|| this.touch.imagePosition == -1 && this.touch.delta < 0) {
			this.touch.gesture = SCROLL_X;
			return cancelAnimationFrame(this.touch.a);
		}
		this.touch.deltaY = this.touch.pageY - this.touch.startY;
		this._.image_container._translateX = this.touch.initialX + this.touch.delta;
		this._.image_container.style.transform = 'translate3d(' + this._.image_container._translateX * this._.image_container.offsetWidth / 100 + 'px,0,0) rotate(0.0001deg)';
		if(this.touch.gesture == SWIPE) return;
		if(Math.abs(this.touch.delta) > 5) {
			//document.body.style.touchAction = 'none';
			this.touch.gesture = SWIPE;
			return;
		}
		if(Math.abs(this.touch.deltaY) > this.touch.em * 1.2) {
			this.touch.gesture = SCROLL;
			this._.image_container._translateX = this.touch.initialX;
			this._.image_container.style.transform = 'translate3d(' + this._.image_container._translateX + '%,0,0)';
			cancelAnimationFrame(this.touch.a);
		}
	}
	
	this._.image_container.ontouchmove = e => {
		this.touch.pageX = e.touches[0].pageX;
		this.touch.pageY = e.touches[0].pageY;
		if(this.touch.gesture == SWIPE)
			{ e.preventDefault(); e.stopPropagation(); }
	}
	
	this._.image_container.ontouchmov = e => {
		if(this.touch.gesture == SCROLL) return;
		if(e.touches.length > 1) return;
		if(Settings.all.layout.get() == 'ttb') return;
		this.touch.delta = e.touches[0].pageX / this._.image_container.offsetWidth * 100 - this.touch.start;
		if(this.touch.imagePosition == 0
		|| this.touch.imagePosition == 1 && this.touch.delta > 0
		|| this.touch.imagePosition == -1 && this.touch.delta < 0)
			return this.touch.gesture = SCROLL_X;
		this.touch.deltaY = e.touches[0].pageY - this.touch.startY;
		this._.image_container._translateX = this.touch.initialX + this.touch.delta;
		requestAnimationFrame(() => {
			this._.image_container.style.transform = 'translate3d(' + this._.image_container._translateX * this._.image_container.offsetWidth / 100 + 'px,0,0) rotate(0.0001deg)';
		})
		if(this.touch.gesture == SWIPE || Math.abs(this.touch.delta) > 5) {
			return this.touch.gesture = SWIPE;
		}
		if(Math.abs(this.touch.deltaY) > this.touch.em * 1.2) {
			this.touch.gesture = SCROLL;
			this._.image_container._translateX = this.touch.initialX;
			this._.image_container.style.transform = 'translate3d(' + this._.image_container._translateX + '%,0,0)';
		}
	}

	this._.image_container.ontouchend = e => {
		if(this.touch.gesture == SCROLL_X || this.touch.gesture == SCROLL) return;
		if(Settings.all.layout.get() == 'ttb') return;
		clearTimeout(this.touch.transitionTimer);
		cancelAnimationFrame(this.touch.a);
		//this._.image_container.style.touchAction = 'unset';
		this._.image_container.style.transition = 'transform 0.25s ease-out';
	var ms = Date.now() - this.touch.time;
	var velocity = this.touch.delta / ms;
		
		if(velocity < this.touch.escapeVelocity * -1
		|| this.touch.delta <this.touch.escapeDelta * -1) {
			setTimeout(() => {
				Settings.all.layout.get() == 'rtl'?
					this.prev():
					this.next();
			}, 1)
		}else{
			if(velocity > this.touch.escapeVelocity
			|| this.touch.delta > this.touch.escapeDelta) {
				setTimeout(() => {
					Settings.all.layout.get() == 'rtl'?
					this.next():
					this.prev();
				}, 1)
			}else{
				this._.image_container._translateX = this.touch.initialX;
				this._.image_container.style.transform = 'translate3d(' + this.touch.initialX + '%,0,0)';
			}
		}
		this.touch.transitionTimer = setTimeout(() => {this._.image_container.style.transition = ''}, 250)
	}

	this.mouseHandler = function(e) {
		if(e.type == 'mousedown') {
			this.mouseHandler.dead = false;
			this.mouseHandler.active = true;
			this.mouseHandler.initPos = {x: e.pageX, y: e.pageY};
			return;
		}
		if(e.type == 'mousemove') {
			if(this.mouseHandler.dead || !this.mouseHandler.active) {
				this.mouseHandler.justHover = true;
			}else{
				if(Math.abs(this.mouseHandler.initPos.x - e.pageX) > 20 ||
				Math.abs(this.mouseHandler.initPos.y - e.pageY) > 20) {
					this.mouseHandler.dead = true;
				}
				return;
			}
		}
		if(e.type == 'click') {
			this.mouseHandler.active = false;
			if(this.mouseHandler.dead) {
				return;
			}
		}
		if(e.type == 'mouseleave') {
			this._.hover_prev.classList.add('nodelay');
			this._.hover_next.classList.add('nodelay');
			this._.hover_prev.classList.remove('viz');
			this._.hover_next.classList.remove('viz');
			setTimeout(t => {
				this._.hover_prev.classList.remove('nodelay');
				this._.hover_next.classList.remove('nodelay');
			}, 1)
			this.mouseHandler.previousArea = null;
			clearTimeout(this.mouseHandler.arrowTimeout);
			return;
		}
		if(e.button != 0) return;
	var box = this.$.getBoundingClientRect();
	var areas = [
			0,
			box.width * 0.35 + box.left,
			box.width * 0.5 + box.left,
			box.width * 0.65 + box.left,
			box.width + box.left
		];
		areas.push(e.pageX);
		areas.sort((a,b) => a - b);
		if(e.type == 'click') {
			switch (areas.indexOf(e.pageX)) {
				case 1:
					if(Settings.all.layout.get() != 'ttb')
						(Settings.all.layout.get() == 'ltr')?
							this.prev(e):
							this.next(e);
					break;
				case 2:
					if(IS_MOBILE)
						Settings.cycle('selectorPinned', ['selector-pinned', 'selector-fade']);
					// else
					// 	if(Settings.all.layout.get() != 'ttb')
					// 		(Settings.all.layout.get() == 'ltr')?
					// 			this.prev(e):
					// 			this.next(e);
					break;
				case 3:
					if(IS_MOBILE)
						Settings.cycle('selectorPinned', ['selector-pinned', 'selector-fade']);
					// else
					// 	if(Settings.all.layout.get() != 'ttb')
					// 		(Settings.all.layout.get() == 'ltr')?
					// 			this.next(e):
					// 			this.prev(e);
					break;
				case 4:
					if(Settings.all.layout.get() != 'ttb')
						(Settings.all.layout.get() == 'ltr')?
							this.next(e):
							this.prev(e);
					break;
				default:
					break;
			}
		}else{
			if(this.mouseHandler.previousArea == areas.indexOf(e.pageX))
				return;
			this.mouseHandler.previousArea = areas.indexOf(e.pageX);
			clearTimeout(this.mouseHandler.arrowTimeout);
			switch (this.mouseHandler.previousArea) {
				case 1:
					if(!IS_MOBILE) {
						if(Settings.all.layout.get() != 'ttb') {
							this._.hover_prev.classList.add('viz');
							this._.hover_next.classList.remove('viz');
							this.mouseHandler.arrowTimeout = setTimeout(t => {
								this._.hover_prev.classList.remove('viz');
								this.mouseHandler.previousArea = null;
							}, 1000) //MAGICNUM
						}
					}
					break;
				case 2:
				case 3:
						this._.hover_prev.classList.remove('viz');
						this._.hover_next.classList.remove('viz');
					break;
				case 4:
					if(!IS_MOBILE) {
						if(Settings.all.layout.get() != 'ttb') {
							this._.hover_next.classList.add('viz');
							this._.hover_prev.classList.remove('viz');
							this.mouseHandler.arrowTimeout = setTimeout(t => {
								this._.hover_next.classList.remove('viz');
								this.mouseHandler.previousArea = null;
							}, 1000) //MAGICNUM
						}
					}
					break;
				default:
					break;
			}
		}
	}

	this.$.onmousedown = e => this.mouseHandler(e);
	this.$.onmousemove = e => this.mouseHandler(e);
	this.$.onclick = e => this.mouseHandler(e);
	this.$.onmouseleave = e => this.mouseHandler(e);

}


function UI_ReaderImageWrapper(o) {
	o=be(o);
	UI_List.call(this, {
		node: o.node,
		kind: ['ReaderImageWrapper'].concat(o.kind || []),
		html: o.html || '<div tabindex="-1"></div>'
	});
	Linkable.call(this);

	this.imageInstances = [];
	this.totalWidth = 0;
	//imageObject = {url, index}
	if(o.imageObjects) {
		o.imageObjects.forEach(img => {
		let image = new UI_ReaderImage({
				url: img.url,
				index: img.index,
				parentWrapper: this
			})
			image.S.link(this);
			this.imageInstances.push(image);
		})
	}else{
		console.error(this, 'No images supplied!')
	}
	this.add(this.imageInstances);

	if(this.imageInstances.length > 1) {
		this.$.classList.add('two-page');
	}

	this.load = function() {
		this.imageInstances.forEach(img => img.load());
	}
	this.getIndices = function() {
		return this.get().map(img => img.index)
	}
	this.checkTooWide = width => {
		this.totalWidth += width;
		if(this.totalWidth > this.$.clientWidth) {
			this.$.classList.add('too-wide');
		}
	}
	this.S.mapIn({
		'imageWidth': this.checkTooWide
	})
	this.S.proxyOut('loaded');
}

function UI_ReaderImage(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['ReaderImage'].concat(o.kind || []),
		html: o.html || '<img src="" />'
	});
	Linkable.call(this);

	this.index = o.index;
	this.url = o.url;
	this.parentWrapper = o.parentWrapper;

	this.onloadHandler = function(e) {
		if(e.type == 'load') {
			this.S.out('loaded', this.index);
			return;
		}
		//if(!IS_MOBILE) dragscroll.reset([this.$])
		//if(this.fore) this._.image.style.background = 'url('+this.fore+') no-repeat scroll 0% 0% / 0%';
	}

	this.watchImageWidth = () => {
		if(this.$.naturalWidth > 0) {
			this.S.out('imageWidth', this.$.offsetWidth);
			cancelAnimationFrame(this.RAF);
			this.RAF = null;
			return;
		}
		requestAnimationFrame(this.watchImageWidth);
	}

	this.load = function() {
		if(this.loaded) return;
		this.RAF = requestAnimationFrame(this.watchImageWidth);
		this.$.loading = 'eager';
		this.$.src = this.url;
		this.$.onload = e => this.onloadHandler(e);
		this.loaded = true;
	}

}

function UI_PageSelector(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['PageSelector'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.keys = new UI_Tabs({
		node: this._.page_keys
	});

	this.render = function(SCP) {
		if(SCP.pageCount != this.keys.$.children.length) {
		var keys = [];
			for (var i = 0; i < SCP.pageCount; i++) {
			var key = new UI_Dummy();
				// key.$.onmouseover = e => this.hoverChange(e);
				key.$.innerHTML = i+1;
				keys.push(key);
			}
			this.keys.clear().add(keys)
		}
		this.keys.select(SCP.page, undefined, undefined, true)
	var keys = this.keys.get();
		keys.forEach((key, i) => {
			if(SCP.visiblePages.indexOf(i) > -1) {
				key.$.classList.add('shown');
			}else{
				key.$.classList.remove('shown');
			}
		})
		this._.page_keys_count.innerHTML = SCP.page + 1 + '/' + (SCP.pageCount);
	}
	this.proxy = function(i) {
		this.S.out('page', i);
	}

	this.displayPreload = function(index) {
		this.keys.$.children[+index].classList.add('preloaded');
	}
	this.clearPreload = function() {
		this.keys.$.children.forEach(key => key.classList.remove('preloaded'));
	}
	// this.hoverChange = function(e){
	// 	this._.page_keys_count.innerHTML = this.keys.$.children.indexOf(e.target) + 1;
	// }

	// this.$.onmouseleave = e => {
	// 	this._.page_keys_count.innerHTML = SCP.page + 1;
	// };

	this.S.mapIn({
		'number': this.proxy,
		'SCP': dpraw(data => this.render(data.payload)),
		'loaded': this.displayPreload
	})


	this.keys.S.link(this);
}

function URLChanger(o) {
	o=be(o);
	Linkable.call(this);

	this.updateURL = function(SCP) {
		setTimeout((function(){
			window.history.replaceState(
				{},
				SCP.chapter
					+ ' - '
					+ SCP.chapterName
					+ ', Page '
					+ (SCP.page + 1)
					+ ' - '
					+ Reader.current.title
					+ ' :: Guya',
				"/reader/series/"
					+ SCP.series
					+ '/'
					+ SCP.chapter.replace('.', '-')
					+ '/'
					+ (SCP.page + 1)
			);
		var newtitle = SCP.chapter
					+ ' - '
					+ SCP.chapterName
					+ ' - '
					+ Reader.current.title
					+ ' :: Guya';
			if(newtitle != document.title) document.title = newtitle;
		}).bind(this), 1)
	}

	this.S.mapIn({
		SCP: this.updateURL
	})
}

function UI_MessageBox(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['MessageBox'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.allowedStyles = ['flash', 'fade', 'slide', 'none']
	this.fadeTime = 500;

	this.timers = [];

	this.displayMessage = function(text, style, time) {
		time = time || 2000;
		style = style || 'flash';
		this.timers.forEach(timer => window.clearTimeout(timer));
		if(this.allowedStyles.indexOf(style) > -1) {
			this.allowedStyles.forEach(style => this.$.classList.remove(style));
			setTimeout(() => {
				this.$.classList.add(style);
				this.$.classList.remove('fadeOut');
			}, 1)
		}
		this.$.innerHTML = text;
		this.timers.push(setTimeout(() => this.$.classList.add('fadeOut'), time));
		this.timers.push(setTimeout(() => {
			this.$.innerHTML = '';
			this.allowedStyles.forEach(style => this.$.classList.remove(style));
		}, time + this.fadeTime));
	}

	this.S.mapIn({
		text: this.displayMessage
	});
}


function UI_FauxDrop(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['FauxDrop'].concat(o.kind || []),
	});
	Linkable.call(this);

	this._.label = this.$.querySelector('label');
	this._.drop = this.$.querySelector('select');

	this.drop = new UI_SimpleList({
		node: this._.drop
	})

	this.handler = e => {
		this._.label.innerHTML = this._.drop.options[this._.drop.selectedIndex].text;
	}

	this.add = this.drop.add.bind(this.drop);
	this.clear = this.drop.clear.bind(this.drop);
	this.get = this.drop.get.bind(this.drop);
	this.set = function (value, dry) {
		this.drop.set(value, dry);
		this.handler();
	}


	this._.drop.addEventListener('change', e => this.handler(e));

	this.S.proxyOut('value', this.drop)
}

function UI_SimpleList(o) {
	o=be(o);
	UI_List.call(this, {
		node: o.node,
		kind: ['SimpleList'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.handler = e => {
		this.S.out('value', this.$.value);
		this.$.blur();
	}

	this.set = function (value, dry) {
		this.$.value = value;
		if(!dry)
			this.S.out('value', this.$.value);
	}

	this.add = function(pairs) {
		this.lastAdded = [];
		pairs.forEach(pair => {
		var item = new UI_SimpleListItem(pair);
			this.$.appendChild(item.$);
			this.lastAdded.push(item);
		});
		return this;
	}

	this.$.onchange = this.handler;


}

function UI_SimpleListItem(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['SimpleListItem'].concat(o.kind || []),
		html: o.html || '<option></option>'
	});
	this.value = o.value;
	this.$.value = o.value;
	if(this.$.innerHTML.length < 1)
		this.$.innerHTML = o.text || o.value || 'List Element';
}


function UI_LodaManager(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['LodaManager'].concat(o.kind || []),
		html: o.html || '<div></div>'
	});
	Linkable.call(this);

	this.library = {
		test: new UI_Loda().S.link(this),
		search: new UI_Loda_Search().S.link(this)
	}

	this.display = function(loda) {
		this.$.classList.remove('hidden');
		this.$.innerHTML = '';
		this.$.appendChild(this.library[loda].$);
		this.$.focus();
		this.library[loda].focus();
	}

	this.close = function() {
		this.$.classList.add('hidden');
		this.$.innerHTML = '';
		Reader.$.focus();
	}

	new KeyListener(this.$)
		.noPropagation(true)
		.attach('close', ['Escape'], this.close.bind(this))

	this.S.mapIn({
		'close': this.close
	})
}

function UI_Loda(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Loda'].concat(o.kind || []),
		html: o.html || '<div class="Loda-window" tabindex="-1"><header data-bind="header"></header><button class="is-ico-button close" data-bind="close"></button><content data-bind="content"></content></div>'
	});
	Linkable.call(this);
	this.manager = o.manager;
	if(o.name) this._.header.innerHTML = o.name;

	this.close = function() {
		this.S.out('close');
	}

	this.focus = function() {
		this.focusElement.focus();
		this.focusElement.select();
	}

	this._.close.onclick = this.close.bind(this)
}

function UI_Loda_Search(o) {
	o=be(o);
	UI_Loda.call(this, {
		node: o.node,
		kind: ['Loda_Search'].concat(o.kind || []),
		name: 'Search',
		html: o.html || `<div class="Loda-window" tabindex="-1"><header data-bind="header"></header><button class="is-ico-button close" data-bind="close"></button><content data-bind="content">
				<input type="text" data-bind="input" placeholder="⌕" />
				<div class="search-tabs" data-bind="tabs">
				</div>
				<div class="list-container" data-bind="container">
					<div class="list" data-bind="lookup"></div>
					<div class="list is-hidden" data-bind="indexer"></div>
				</div>
			</content></div>`
	});
	this.manager = o.manager;
	this.name = 'Indexer';
	this.focusElement = this._.input;
	this.container = new UI_ContainerList({
		node: this._.container
	});

	this.lookup = new UI_MangaSearch({
		node: this._.lookup
	})
	this.indexer = new UI_IndexSearch({
		node: this._.indexer
	})

	this.tabs = new UI_Tabs({
			node: this._.tabs
		})
		.add(new UI_Tab({
			text: 'Title search'
		}))
		.add(new UI_Tab({
			text: 'Text search',
			counterText: 'Press <span class="inline-icon">⮠</span>'
		}))
		.S.link(this.container)
		.S.linkAnonymous('number', num => {
			this._.input.focus();
		});
	this.tabs.get(1).$.onmousedown = e => {
		this.input.handler(e);
	}
	this.tabs.select(0);

	this.lookup.S.link(this.tabs.get(0));
	this.indexer.S.link(this.tabs.get(1));
	this.input = new UI_Input({
		node: this._.input
		})
		.S.link(this.lookup)
		.S.link(this.indexer)
		.S.linkAnonymous('text', text => {
			this.tabs.select(1);
			this.tabs.get(1).update('Loading...');
		})

}


function UI_IndexSearch(o) {
	o=be(o);
	UI_Tabs.call(this, {
		node: o.node,
		kind: ['IndexSearch'].concat(o.kind || []),
		html: o.html || `<div></div>`
	});
	Loadable.call(this);

	this.search = function(query) {
		if(query.length < 3) {
			return this.clear();
		}
		API.requestIndex({
			query: query,
			slug: Reader.SCP.series
		}).then(data => {
			for(var searchWord in data.result) {
			var searchResult = data.result[searchWord];
				if(!searchResult._merged) searchResult._merged = {};
				for(var wordVariant in searchResult) {
				var chapters = searchResult[wordVariant];
					if(wordVariant[0] == '_') continue;
					for(var chapter in chapters) {
					var pageList = chapters[chapter];
						if(!searchResult._merged[chapter])
							searchResult._merged[chapter] = pageList || [];
						else {
							pageList.forEach(page => {
								if(searchResult._merged[chapter].indexOf(page) < 0)
									searchResult._merged[chapter].push(page);
							})
						}
					}
				}
			}

		var wordAddrMap = {};
			if(Object.keys(data.result).length > 1) {
				for(var word in data.result) {
				var chapters = data.result[word]._merged;
					for(var chapter in chapters) {
					var pageArray = chapters[chapter];
						pageArray.forEach(page => {
						var id = '' + chapter + '/' + page;
							if(!wordAddrMap[id]) wordAddrMap[id] = 0;
							wordAddrMap[id] += 1;
						})
					}
				}
			var wordAddrMap = Object.filter(wordAddrMap, id => {
					return id == Object.keys(data.result).length;
				})
			var chapters = {};
				for(var key in wordAddrMap) {
				var id = key.split('/')
					if(!chapters[id[0]]) chapters[id[0]] = [];
					chapters[id[0]].push(id[1]);
				}
			}else{
				chapters = data.result[Object.keys(data.result)[0]]._merged;
			}


			// if(Object.keys(data.result).length > 1) {
			// var chapters = Object.keys(data.result[firstWord]._merged).filter((item, key) => {
			// 		for(var word in data.result) {
			// 			if(word == firstWord) continue;
			// 		var chapters = Object.keys(data.result[word]._merged);
			// 			if(chapters.indexOf(item) < 0)
			// 				return false;
			// 		}
			// 		return true;
			// 	})	
			// }else{
			// 	var chapters = Object.keys(data.result[firstWord]._merged);
			// }

		var chapterElements = [];
		var chapKeys = Object.keys(chapters).sort((a,b) => parseFloat(a) - parseFloat(b));
			for(var i=0;i<chapKeys.length;i++) {
			var key = chapKeys[i];
			var item = chapters[key];
				try{
				chapterElements.push(new UI_ChapterUnit({
					chapter: Reader.current.chapters[key.replace('-', '.')],
				//	substring: Object.keys(data.result)[0],
					pages: item.sort((a,b) => a-b)
				}))	
				}catch(e){
					console.warn('Chapter', key, 'wasn\'t found?')
				}	
			};

			this.clear().add(chapterElements);

		}).catch(err => {throw new Error(err)})

	}

	this.S.mapIn({
		'text': this.search,
		// 'quickText': this.clear
	})
}
function UI_MangaSearch(o) {
	o=be(o);
	UI_Tabs.call(this, {
		node: o.node,
		kind: ['MangaSearch'].concat(o.kind || []),
		html: o.html || `<div></div>`
	});

	this.search = function(query, force) {
	this.query = query;
		if(query.length < 1) {
			this.clear(); return;
		}
		if(this.debounce) {
			clearTimeout(this.debouncer);
			this.debouncer = setTimeout(e => {
				this.debounce = false;
				this.search(this.query, true);
			}, 200);
			return;
		}
		if(!force) this.debounce = true;

	var chapters = {};
		if(isNaN(this.query) == false) {
			Reader.current.chaptersIndex.filter(id => {
				return (''+id).indexOf(this.query) > -1;
			}).map(id => {
				return Reader.current.chapters[id];
			}).forEach(chapter => {
				chapters[chapter.id] = chapter;
			})
		}else{
			if(this.query.length < 3) return;
		}
		for(var id in Reader.current.chapters) {
		var chapter = Reader.current.chapters[id];
			if(chapter.title.toLowerCase().indexOf(this.query.toLowerCase()) > -1) {
				chapters[id] = chapter;
			}
		}
	var chapterElements = [];
		for(var id in chapters) {
		var chapter = chapters[id];
			chapterElements.push(new UI_ChapterUnit({
				chapter: chapter,
				substring: query
			}))
		}
		
		this.clear().add(chapterElements);
	}

	this.S.mapIn({
		'text': this.search,
		'quickText': this.search
	})
}


function UI_ChapterUnit(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['ChapterUnit'].concat(o.kind || []),
		name: 'ChapterUnit',
		html: o.html || `<div><figure data-bind="figure"></figure><content><h2 data-bind="title"></h2><blockquote data-bind="text"></blockquote><div class="pages" data-bind="pages"></div></content></div>`
	});

	this.chapter = o.chapter;
	this.pages = o.pages;
	this.substring = o.substring
	this.pageList = new UI_Tabs({
		node: this._.pages
	})
	this._.title.innerHTML = (o.chapter.id + ' - ' + o.chapter.title).replace(new RegExp('('+o.substring+')', 'gi'), '<i>$1</i>');
	for(var group in o.chapter.images) {
		this._.figure.style.backgroundImage = 'url('+(this.pages?o.chapter.previews[group][+this.pages[0]-1]:o.chapter.previews[group][0])+')';
		break;
	}
	if(this.pages) {
		this.pages.forEach(page => {
		var pageButton = new UI_Dummy({text: page});
			pageButton.$.onclick = e => {
				e.stopPropagation();
				e.preventDefault();
				Reader.drawChapter(this.chapter.id, +e.target.innerHTML-1);
				Loda.close();
				return false;
			}
			this.pageList.add(pageButton);
		})
	}

	this.$.onclick = e => {
		Reader.drawChapter(this.chapter.id, 0);
		Loda.close();
	}
}





alg.createBin();

API = new ReaderAPI();
Settings = new SettingsHandler();
Tooltippy = new UI_Tooltippy({
	node: document.querySelector('.Tooltippy'),
});
Reader = new UI_Reader({
	node: document.getElementById('rdr-main'),
});
Loader = new LoadHandler();
URL = new URLChanger();
Loda = new UI_LodaManager({
	node: document.querySelector('.LodaManager'),
});

API.S.link(Reader);
Settings.S.link(Reader);
Reader.S.link(URL)
Reader.S.link(Settings)
Reader.$.focus()
if(window.location.hash == '#s') Loda.display('search');
document.body.ontouchstart = e=>{}
function debug() {
}
