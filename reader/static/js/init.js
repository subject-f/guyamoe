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

	document.body.onload = this.onload;
}

function ReaderAPI(o) {
	o=be(o);
	Linkable.call(this);

	this.url = o.url || '/api/';
	this.seriesUrl =  this.url + 'series/';
	this.mediaURL = o.mediaURL || '/media/manga/';

	this.data = {};

	this.infuseImageURLs = function(data) {
		for(var num in data.chapters) {
		var chapter = data.chapters[num];
			chapter.images = {};
			chapter.blurs = {};
			chapter.previews = {};
			for(var group in chapter.groups) {
				chapter.images[group] = [];
				chapter.blurs[group] = [];
				chapter.previews[group] = [];
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
							+ "shrunk_blur_"+group 
							+ '/' 
							+ chapter.groups[group][i]
					)
					chapter.previews[group].push(
						this.mediaURL
							+ data.slug 
							+ '/chapters/' 
							+ chapter.folder 
							+ '/' 
							+ "shrunk_"+group 
							+ '/' 
							+ chapter.groups[group][i]
					)
				}
			}
		}
		return data;
	}

	this.requestSeries = function(slug) {
		this.seriesRequest = fetch(this.seriesUrl + slug)
			.then(response => response.json())
			.then(seriesData => {
				seriesData = this.infuseImageURLs(seriesData);
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
			})
			.then(o => {
				return fetch(this.url + 'get_groups/' + slug)
			})
			.then(response => response.json())
			.then(o => {
				this.data[slug].groups = o.groups;
				this.S.out('seriesUpdated', this.data[slug]);
			})
		return this.seriesRequest;
	}

	this.S.mapIn({
		'loadSeries': this.requestSeries
	})
	this.S.mapOut(['seriesUpdated'])
}

function SettingsHandler(){
	Linkable.call(this);

	this.all = {};

	this.all.fit = new Setting(
		'fit',
		'Page fit',
		['fit-width', 'fit-height', 'fit-none'],
		(IS_MOBILE)?'fit-width':'fit-none',
		{
			'fit-width': 'Images fit to width.',
			'fit-height': 'Images fit to height.',
			'fit-none': 'Images are displayed in original size.'
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
	this.all.groupPreference = new Setting(
		'groupPreference',
	)
	this.all.selectorPinned = new Setting(
		'selectorPinned',
		'Page selector',
		['show', 'hide'],
		'hide',
		{
			'show': 'Page selector is always visible.',
			'hide': 'Page selector is shown on hover.'
		}
	)
	this.all.preload = new Setting(
		'preload',
		'Preload amount',
		[1,2,3,4,5,6,7,8],
		2,
		i => 'Reader will preload %i pages.'.replace('%i', i).replace('1 pages', '1 page')
	)
	this.all.sidebar = new Setting(
		'sidebar',
		'Sidebar',
		['hide', 'show'],
		'show',
		{
			'hide': 'Sidebar hidden.',
			'show': 'Sidebar shown.',
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

	for (var key in this.all) {
		this.all[key].super = this;
	}

	this.serialize = function() {
	var settings = {};
		for(var setting in this.all) {
			settings[setting] = this.all[setting].get();
		}
		settings.VER = this.ver;
		return JSON.stringify(settings);
	}

	this.deserialize = function() {
		if(!window.localStorage) return;
	var settings = window.localStorage.getItem('settings');
		if(!settings) return;
		try{
			settings = JSON.parse(settings);
			for(var setting in settings) {
				if(setting == 'VER') {
					if(settings[setting] != this.ver) {
						throw 'Settings ver changed';
					}
					continue;
				}
				this.all[setting].set(settings[setting], true);
			}
		}catch (e){
			localStorage.setItem('settings','');
			console.warn('Settings were found to be corrupted and so were reset.')
		}
	}

	this.settingUpdated = function(setting) {
		if(window.localStorage)
			window.localStorage.setItem('settings', this.serialize())
		this.S.out('setting', {setting: setting.name, value: setting.get()})
		this.S.out('message', setting.getFormatted());
	}

	this.ver = '0.4';

	this.deserialize();

	this.S.mapOut(['setting', 'message']);
}

function Setting(name, prettyName, options, dflt, strings) {
	this.name = name;
	this.prettyName = prettyName;
	this.setting = dflt;
	this.options = options;
	this.strings = strings;
	this.cycle = function() {
		if(this.options) {
		var index = this.options.indexOf(this.setting);
			this.set(
				(index+1 > this.options.length - 1)?this.options[0]:this.options[index+1]
			);
		}
		return this;
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
		if(this.strings instanceof Function) {
			return this.strings(this.setting);
		}
		return this.strings[this.setting];
	}
	this.set = function(value, silent) {
		if(value == this.setting) return;
		if(this.options) {
			if(this.options.indexOf(value) < 0)
				throw new Error('A setting must be one of: ' + this.options.join(', '))
		}
		this.setting = value;
		if(!silent)
			this.super.settingUpdated(this);
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
	

	new KeyListener()
		.pre(() => this._.image_container.focus())
		.attach('prevCh', ['BracketLeft'], e => this.prevChapter())
		.attach('nextCh', ['BracketRight'], e => this.nextChapter())
		.attach('fit', ['KeyF'], e => Settings.all.fit.cycle())
		.attach('layout', ['KeyD'], e => Settings.all.layout.cycle())
		.attach('sidebar', ['KeyS'], s => Settings.all.sidebar.cycle())
		.attach('pageSelector', ['KeyN'], s => Settings.all.selectorPinned.cycle())
		.attach('preload', ['KeyL'], s => Settings.all.preload.cycle())
		.attach('minus', ['Minus'], s => {
			Settings.all.fit.set('fit-width')
			Settings.all.zoom.next()
		})
		.attach('plus', ['Equal'], s => {
			Settings.all.fit.set('fit-width')
			Settings.all.zoom.prev()
		})
		.attach('previews', ['KeyP'], s => Settings.all.previews.cycle())

	new KeyListener()
		.condition(() => Settings.all.layout.get() == 'ltr')
		.pre(() => this._.image_viewer.querySelector('.is-active').focus())
		.attach('prev', ['ArrowLeft'], e => this.prevPage())
		.attach('next', ['ArrowRight'], e => this.nextPage());

	new KeyListener()
		.condition(() => Settings.all.layout.get() == 'rtl')
		.pre(() => this._.image_viewer.querySelector('.is-active').focus())
		.attach('prev', ['ArrowRight'], e => this.prevPage())
		.attach('next', ['ArrowLeft'], e => this.nextPage());

	this.selector_chap = new UI_SimpleList({
		node: this._.selector_chap
	}).S.linkAnonymous('value', value => {
		this.SCP.page = 0;
		this.drawChapter(value);
	});
	this.selector_vol = new UI_SimpleList({
		node: this._.selector_vol
	}).S.linkAnonymous('value', value => this.selectVolume(value));
	this.imageView = new UI_ReaderImageView({
		node: this._.image_viewer
	}).S.link(this);
	this.groupList = new UI_Tabs({
		node: this._.groups
	}).S.linkAnonymous('id', id => this.drawGroup(id));
	this.selector_page = new UI_PageSelector({
		node: this._.page_selector
	}).S.linkAnonymous('page', id => this.displayPage(id));
	this.messageBox = new UI_MessageBox({
		node: this._.message
	})
	this.previews = new UI_Tabs({
		node: this._.previews
	}).S.linkAnonymous('number', id => this.displayPage(id));

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
		this.SCP.page = SCP.page;
		this.drawChapter(SCP.chapter);
	}

	this.drawReader = function(slug) {
		if(slug) this.SCP.series = slug;
		this._.title.innerHTML = this.current.title;
	var chapterElements = [];
	var volElements = {};
		for (var i = this.current.chaptersIndex.length - 1; i >= 0; i--) {
		var chapterNumber = this.current.chaptersIndex[i];
		var chapter = this.current.chapters[chapterNumber];
			chapterElements.push(new UI_SimpleListItem({
				text: chapterNumber + ' - ' + chapter.title,
				value: chapterNumber
			}));

		}
		volElements = Object.keys(this.current.volMap).sort((a,b) => parseFloat(b) - parseFloat(a)).map(item => {
			return new UI_SimpleListItem({
				value: item,
			})
		});

		this.selector_chap.clear().add(chapterElements);
		this.selector_vol.clear().add(volElements);

		this.setFit(Settings.all.fit.get());
		this.setLayout(Settings.all.layout.get(), true);
		this.setSelectorPin(Settings.all.selectorPinned.get());
		this.setPreload(Settings.all.preload.get());
		this.setSidebar(Settings.all.sidebar.get());
		this.setZoom(Settings.all.zoom.get());
		setTimeout(() => {
			this._.page_selector.classList.remove('vis')
			this._.zoom_level.classList.remove('vis')
		}, 3000);
		this._.close.href = '/reader/series/' + this.SCP.series;
	}

	this.drawGroup = function(group) {
		Settings.all.groupPreference.set(group);
		this.drawChapter()
	}

	this.drawChapter = function(chapter) {
		if(chapter) this.SCP.chapter = chapter;
	var chapterObj = this.current.chapters[this.SCP.chapter];
		this.SCP.volume = chapterObj.volume;
	var group = Settings.all.groupPreference.get();
		if(group === undefined || chapterObj.groups[group] == undefined) {
			group = Object.keys(chapterObj.groups)[0];
		}
		this.SCP.group = group;
		this.SCP.pageCount = chapterObj.groups[group].length;

		this.groupList.clear();
	var groupElements = {};
		for(var grp in chapterObj.groups) {
			groupElements[grp] = new UI_SimpleListItem({
				html: '<div' + ((grp==group)?' class="is-active"':'') + '></div>',
				text: this.current.groups[grp]
			})
		}
		this.groupList.addMapped(groupElements);

		this.imageView.drawImages(chapterObj.images[group]);
		this.selector_chap.$.value = this.SCP.chapter;
		this.selector_vol.$.value = chapterObj.volume;
		this._.page_selector.classList.add('vis')
		setTimeout(() => this._.page_selector.classList.remove('vis'), 2000);
		this.plusOne();
		this.selector_page.clearPreload();
		this.displayPage();
		this.showPreviews(Settings.all.previews.get());
		return this;
	}

	this.displayPage = function(page, dry) {
		if(page == 'last')
			this.SCP.page = this.current.chapters[this.SCP.chapter].images[this.SCP.group].length - 1;
		else
			if(page !== undefined) this.SCP.page = page;
		this.imageView.selectPage(this.SCP.page, dry);
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
	var formData = new FormData();
		formData.append("series", this.current.slug)
		formData.append("group", this.SCP.group)
		formData.append("chapter", this.SCP.chapter)
		formData.append("csrfmiddlewaretoken", CSRF_TOKEN)
		fetch('/reader/update_view_count/', {
			method: 'POST',
			body: formData, // body data type must match "Content-Type" header
		})
	}


	this.nextChapter = function(){
		if(this.SCP.chapter < this.current.chaptersIndex.length - 1) {
		var index = this.current.chaptersIndex.indexOf(''+this.SCP.chapter);
			if(index < 0) throw new Error('Chapter advance failed: invalid base index.')
			this.SCP.page = 0;
			this.drawChapter(
				this.current.chaptersIndex[index + 1]
			)
		}
		this.messageBox.displayMessage('Next chapter.', 'fade');
	}
	this.prevChapter = function() {
		if(this.SCP.chapter > 1)
		var index = this.current.chaptersIndex.indexOf(''+this.SCP.chapter);
			if(index < 0) throw new Error('Chapter stepback failed: invalid base index.')
			this.SCP.page = 0;
			this.drawChapter(
				this.current.chaptersIndex[index - 1]
			)
			this.messageBox.displayMessage('Previous chapter.', 'fade');
	}
	this.nextPage = function(){
		if(this.SCP.page < this.current.chapters[this.SCP.chapter].images[this.SCP.group].length - 1) 
			this.displayPage(this.SCP.page + 1)
		else {
			this.nextChapter();
		}
	}
	this.prevPage = function(){
		if(this.SCP.page > 0) 
			this.displayPage(this.SCP.page - 1)
		else {
			this.prevChapter();
			this.displayPage('last');
		}
	}
	this.nextVolume = function(){
		this.selectVolume(+this.SCP.volume+1);
		this.messageBox.displayMessage('Next volume.', 'fade');
	}
	this.prevVolume = function(){
		this.selectVolume(+this.SCP.volume-1)
		this.messageBox.displayMessage('Previous volume.', 'fade');
	}

	this.setFit = function(fit) {
		Settings.all.fit.options.forEach(item => {
			this.$.classList.remove(item);
			this._.fit_button.classList.remove(item);
		});
		this.$.classList.add(fit);
		this._.fit_button.classList.add(fit);
	}

	this.setLayout = function(layout, silent) {
		Settings.all.layout.options.forEach(item => {
			this.$.classList.remove(item);
		});
		this.$.classList.add(layout);

		if(!silent) {
			this.imageView.drawImages(this.current.chapters[this.SCP.chapter].images[this.SCP.group]);
			this.imageView.selectPage(this.SCP.page);
		}
	}

	this.setSelectorPin = function(state) {
		if(state == 'show') {
			this.$.classList.add('selector-pinned');
		}else{
			this.$.classList.remove('selector-pinned');
		}
	}

	this.setPreload = function(number){
		this.$.setAttribute('data-preload', number);
	}

	this.setZoom = function(zoom) {
		Settings.all.zoom.options.forEach(item => {
			this.$.classList.remove('zl'+item);
		});
		this.$.classList.add('zl'+zoom);
	}

	this.setSidebar = function(state) {
		if(state == 'hide') {
			this.$.classList.add('sidebar-hidden');
		}else{
			this.$.classList.remove('sidebar-hidden');
		}
	}

	this.eventRouter = function(event){
		({
			'nextPage': () => this.nextPage(),
			'prevPage': () => this.prevPage()
		})[event.type](event.data)
	}

	this.settingsRouter = function(o) {
		({
			'fit': o => this.setFit(o),
			'layout': o => this.setLayout(o),
			'groupPreference': o => {},
			'selectorPinned': o => this.setSelectorPin(o),
			'preload': o => this.setPreload(o),
			'sidebar': o => this.setSidebar(o),
			'previews': o => this.showPreviews(o),
			'zoom': o => this.setZoom(o),
		})[o.setting](o.value)
	}

	this._.chap_prev.onmousedown = e => this.prevChapter(e);
	this._.chap_next.onmousedown = e => this.nextChapter(e);
	this._.vol_prev.onmousedown = e => this.prevVolume(e);
	this._.vol_next.onmousedown = e => this.nextVolume(e);
	this._.preload_button.onmousedown = e => Settings.all.preload.cycle();
	this._.layout_button.onmousedown = e => Settings.all.layout.cycle();
	this._.fit_button.onmousedown = e => Settings.all.fit.cycle();
	this._.sel_pin_button.onmousedown = e => Settings.all.selectorPinned.cycle();
	this._.sidebar_button.onmousedown = e => Settings.all.sidebar.cycle();
	this._.previews_button.onmousedown = e => Settings.all.previews.cycle();
	this._.zoom_level_plus.onmousedown = e => Settings.all.zoom.next();
	this._.zoom_level_minus.onmousedown = e => Settings.all.zoom.prev();

	this.S.mapIn({
		seriesUpdated: this.updateData,
		event: this.eventRouter,
		setting: this.settingsRouter,
		message: message => this.messageBox.displayMessage(message),
	})
	this.S.mapOut(['SCP']);

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

	this.drawImages = function(images) {
		this.imageContainer.clear();
	var imageInstances = [];
		images.forEach((url, index) => {
			imageInstances.push(new UI_WrappedImage({src: url, index: index, fore: images[index+1]}));
		})
		imageInstances.forEach(image => {
			image.S.link(Reader.selector_page);
		})
		this.imageContainer.add(imageInstances);
		if(Settings.all.layout.get() == 'rtl') this.imageContainer.reverse();
	}

	this.selectPage = function(index, dry) {
		if(index < 0 || index >= this.imageContainer.$.children.length)
			return;
	var pageElement = this.$.querySelector('*[data-index="'+index+'"]')
	var realIndex = this.imageContainer.$.children.indexOf(pageElement);
		this.imageContainer.select(realIndex);
	var direction = (Settings.all.layout.get() == 'rtl')?-1:1;
		for(var i = -1; i < Settings.all.preload.get() + 1; i++){
		var image = this.imageContainer.get(i*direction + realIndex);
			if(image) image.load(); else continue;
		}
		if(Settings.all.layout.get() == 'ttb'){
			if(!dry) {
				this._.image_container.scrollTo({
					left: 0,
					top: pageElement.offsetTop
				})
				if(pageElement.offsetTop > 0)
					document.documentElement.scrollTo({
						left: 0,
						top:
							Math.round(
								pageElement.offsetTop
								+ (this._.image_container.getBoundingClientRect()).top
							)
					})
			}
		}else{
			this.imageContainer.$.style.left = -1 * 100 * realIndex - 0.001 + '%';
			//setTimeout(() => scrollToY(this.$, 0, 0.15, 'easeInOutSine'), 150)
			// setTimeout(() => {
				// this.imageContainer.selectedItems[0].$.style.top = 0;
			pageElement.scrollTo({
				left: 0,
				top: 0
			})
			// }, 150)
		}
	}

	this.prev = function() {
		this.S.out('event', {type: 'prevPage'});

	}
	this.next = function() {
		this.S.out('event', {type: 'nextPage'})
	}


	document.onscroll = this._.image_container.onscroll = e => {
		if(Settings.all.layout.get() == 'ttb') {

		var st = (
				(e.target.scrollingElement)?
					e.target.scrollingElement.scrollTop:
					undefined
				|| e.target.scrollTop
			) + 1;
		var offsets = this.imageContainer.$.children.map(item => item.offsetTop);
			offsets.push(st);
			offsets = offsets.sort((a, b) => a - b);
		var index = offsets.indexOf(st) - 1;
			if(Reader.SCP.page == index) return;
			Reader.displayPage(index, true);
			return;
		}else{
			if(this.imageContainer.selectedItems[0].$.nextSibling)
				this.imageContainer.selectedItems[0].$.nextSibling.style.top = this.$.scrollTop + 'px';
			if(this.imageContainer.selectedItems[0].$.prevSibling)
				this.imageContainer.selectedItems[0].$.prevSibling.style.top = this.$.scrollTop + 'px';
		}
	}
	this.mouseHandler = function(e) {
		if(Settings.all.layout.get() == 'ttb') return;
		if(e.button != 0) return;
	var box = this.$.getBoundingClientRect();
	var cutoff = box.width * 0.35 + box.left;
	var scroll = box.width + box.left - 30;
		if(e.pageX > cutoff) {
			if(e.pageX < scroll)
				(Settings.all.layout.get() == 'ltr')?
					this.next(e):
					this.prev(e);
		}else if(e.pageX > box.left){
			(Settings.all.layout.get() == 'ltr')?
				this.prev(e):
				this.next(e);
		}
	}

	this.$.onmousedown = e => this.mouseHandler(e);

	this.S.mapOut(['event']);
}


function UI_WrappedImage(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['WrappedImage'].concat(o.kind || []),
		html: o.html || '<div><img data-bind="image" src="" /></div>'
	});
	Linkable.call(this);

	this.src = o.src;
	this.loaded = false;
	this.index = o.index;
	this.fore = o.fore;

	this.onloadHandler = function(e) {
		this.S.out('loaded', this.index);
		if(this._.image.getBoundingClientRect().width > this.$.getBoundingClientRect().width) {
			this.$.classList.add('too-wide');
		}
	}

	this.load = function() {
		if(this.loaded) return;
		this._.image.src = this.src;
		this._.image.onload = e => this.onloadHandler(e);
		this.loaded = true;
		this._.image.style.background = 'url('+this.fore+') no-repeat scroll 0% 0% / 0%';
	}

	this.$.setAttribute('data-index', this.index);

	this.S.mapOut(['loaded'])
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
		// this._.page_keys_count.innerHTML = SCP.page + 1;
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
		'SCP': this.render,
		'loaded': this.displayPreload
	})
	this.S.mapOut(['page'])

	this.keys.S.link(this);
}

function URLChanger(o) {
	o=be(o);
	Linkable.call(this);

	this.updateURL = function(SCP) {
		window.history.replaceState(
			{},
			Reader.current.title
				+ ' - Chapter '
				+ SCP.chapter
				+ ', Page '
				+ (SCP.page + 1),
			"/reader/series/"
				+ SCP.series
				+ '/'
				+ SCP.chapter.replace('.', '-')
				+ '/'
				+ (SCP.page + 1)
		);
		document.title = Reader.current.title
				+ ' - Chapter '
				+ SCP.chapter
				+ ', Page '
				+ (SCP.page + 1)
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

	this.allowedStyles = ['flash', 'fade', 'slide']
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

function UI_SimpleList(o) {
	o=be(o);
	UI_List.call(this, {
		node: o.node,
		kind: ['SimpleList'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.handler = e => {
		this.S.out('value', this.$.value)
		this.$.blur();
	}



	this.add = function(uiInstances) {
		this.lastAdded = [];
		uiInstances.forEach(item => {
			this.$.appendChild(item.$);
			this.lastAdded.push(item);
		});
		return this;
	}

	this.$.onchange = this.handler;

	this.S.mapOut(['value'])
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

alg.createBin();

API = new ReaderAPI();
Settings = new SettingsHandler();
Reader = new UI_Reader({
	node: document.getElementById('rdr-main'),
});
Loader = new LoadHandler();
URL = new URLChanger();

API.S.link(Reader);
Settings.S.link(Reader);
Reader.S.link(URL)