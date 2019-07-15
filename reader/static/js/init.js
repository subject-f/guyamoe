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
			for(var group in chapter.groups) {
				chapter.images[group] = [];
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
		'fit-none'
	)
	this.all.layout = new Setting(
		'layout',
		'Reader layout',
		['ltr', 'ttb', 'rtl'],
		'ltr'
	)
	this.all.groupPreference = new Setting(
		'groupPreference',
	)
	this.all.selectorPinned = new Setting(
		'selectorPinned',
		'Page selector',
		['persist', 'fade'],
		'fade'
	)
	this.all.preload = new Setting(
		'preload',
		'Preload amount',
		[1,2,3,4,5],
		'1'
	)

	for (var key in this.all) {
		this.all[key].super = this;
	}

	this.serialize = function() {
	var settings = {};
		for(var setting in this.all) {
			settings[setting] = this.all[setting].get();
		}
		return JSON.stringify(settings);
	}

	this.deserialize = function() {
		if(!window.localStorage) return;
	var settings = window.localStorage.getItem('settings');
		if(!settings) return;
		settings = JSON.parse(settings);
		for(var setting in settings) {
			this.all[setting].set(settings[setting], true);
		}
	}

	this.settingUpdated = function(setting) {
		if(window.localStorage)
			window.localStorage.setItem('settings', this.serialize())
		this.S.out('setting', {setting: setting.name, value: setting.get()})
		this.S.out('message', setting.prettyName + ' changed to ' + setting.get());
	}

	this.deserialize();

	this.S.mapOut(['setting', 'message']);
}

function Setting(name, prettyName, options, dflt) {
	this.name = name;
	this.prettyName = prettyName;
	this.setting = dflt;
	this.options = options;
	this.cycle = function() {
		if(this.options) {
		var index = this.options.indexOf(this.setting);
			this.set(
				(index+1 > this.options.length - 1)?this.options[0]:this.options[index+1]
			);
		}
		return this;
	}
	this.get = function() {
		return this.setting;
	}
	this.set = function(value, silent) {
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
		.attach('cycleFit', ['KeyF'], e => Settings.all.fit.cycle())
		.attach('cycleLayout', ['KeyL'], e => Settings.all.layout.cycle())

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
		this.drawChapter(SCP.chapter);
		this.displayPage(SCP.page);
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
		setTimeout(() => this._.page_selector.classList.remove('vis'), 3000);
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
		this.displayPage();
		this._.page_selector.classList.add('vis')
		setTimeout(() => this._.page_selector.classList.remove('vis'), 2000);
		this.plusOne();
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
		if(this.SCP.chapter < this.current.chaptersIndex.length - 2) {
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
			this.imageView.$.classList.remove(item);
			this._.fit_button.classList.remove(item);
		});
		this.imageView.$.classList.add(fit);
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
		if(state == 'persist') {
			this.$.classList.add('selector-pinned');
		}else{
			this.$.classList.remove('selector-pinned');
		}
	}

	this.setPreload = function(number){
		this.$.setAttribute('data-preload', number);
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

	this.S.mapIn({
		seriesUpdated: this.updateData,
		event: this.eventRouter,
		setting: this.settingsRouter,
		message: message => this.messageBox.displayMessage(message),
	})
	this.S.mapOut(['SCP']);

	this.S.link(this.selector_page);
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
		images.forEach((url, index) => {
			this.imageContainer.add(new UI_WrappedImage({src: url, index: index, fore: images[index+1]}))
		})
		if(Settings.all.layout.get() == 'rtl') this.imageContainer.reverse();
	}

	this.selectPage = function(index, dry) {
		if(index < 0 || index >= this.imageContainer.$.children.length)
			return;
	var pageElement = this.$.querySelector('*[data-index="'+index+'"]')
	var realIndex = this.imageContainer.$.children.indexOf(pageElement);
		this.imageContainer.select(realIndex);
		if(Settings.all.layout.get() == 'ttb'){
			if(!dry)
				this._.image_container.scrollTo({
					left: 0,
					top: pageElement.offsetTop
				})
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


	this._.image_container.onscroll = e => {
		if(Settings.all.layout.get() == 'ttb') {
		var st = this._.image_container.scrollTop + 1;
		var offsets = this.imageContainer.$.children.map(item => item.offsetTop);
			offsets.push(st);
			offsets = offsets.sort((a, b) => a - b);
			Reader.displayPage(offsets.indexOf(st) - 1, true);
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
	// this.hoverChange = function(e){
	// 	this._.page_keys_count.innerHTML = this.keys.$.children.indexOf(e.target) + 1;
	// }

	// this.$.onmouseleave = e => {
	// 	this._.page_keys_count.innerHTML = SCP.page + 1;
	// };

	this.S.mapIn({
		'number': this.proxy,
		'SCP': this.render
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

function UI_WrappedImage(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['WrappedImage'].concat(o.kind || []),
		html: o.html || '<div><img data-bind="image" src="" /></div>'
	});

	this._.image.src = o.src;
	this.$.setAttribute('data-index', o.index);
	this._.image.style.background = 'url('+o.fore+') no-repeat scroll 0% 0% / 0%';
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