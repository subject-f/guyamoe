function LoadHandler(o) {
	o=be(o);
	Linkable.call(this);

	this.parseSCP = function(url) {
		url = url.split('/');
		return {
			page: parseInt(url[url.length - 1] - 1),
			chapter: url[url.length - 2].replace('-','.'),
			series: url[url.length - 3],
		}
	}

	this.onload = () => {
	var SCP = this.parseSCP(document.location.pathname);
		Action.displaySCP(SCP);
	}

	document.body.onload = this.onload;
}


function ActionHandler(o) {
	o=be(o);
	Linkable.call(this);
	this.url = o.url;
	this.mediaURL = o.mediaURL;

	this.infuseImageURLs = function(data) {
		for(var num in data.chapters) {
		var chapter = data.chapters[num];
			chapter.images = [];
			for (var i = 0; i < chapter.pages.length; i++) {
				chapter.images.push(this.mediaURL + data.slug + '/' + chapter.folder + '/' + (chapter.pages[i]))
			}
		}
		return data;
	}

	this.displaySeries = function(slug) {
		this.seriesRequest = fetch(this.url + 'series/' + slug)
			.then(response => response.json())
			.then(seriesData => {
					seriesData = this.infuseImageURLs(seriesData);
					seriesData.chaptersIndex =
						Object.keys(
							seriesData.chapters
						).sort((a,b) => parseFloat(b) - parseFloat(a));
					this.S.out('series_data', o);
					this.S.out('state_series', slug)
			})
		return this;
	}

	this.displayChapter = function(id) {
		this.S.out('state_chapter', id);
		return this;
	}

	this.displayPage = function(id) {
		this.S.out('state_page', id);
		return this;
	}

	this.displaySCP = function(SCP) {
		if(SCP.series) this.displaySeries(SCP.series);
		if(SCP.chapter) this.displayChapter(SCP.chapter);
		if(SCP.page) this.displayPage(SCP.page);
		return this;
	}

	this.S.mapOut([
		'series_data',
		'state_series',
		'state_chapter',
		'state_page'
	]);
}

function Reader_StorageHandler(o) {
	o=be(o);
	Linkable.call(this);

	this.series = {};
	this.chapter = null;
	this.page = null;

	this.storeSeries = function(data) {
		this.series = data.slug;
		this.seriesObject = data;
		this.S.out('data', this.series)
	}

	this.updateChapter = function(chapterNumber) {
		this.chapter = chapterNumber;
		this.chapterObject = this.series[this.chapter];
		this.S.out('state_chapter', this.chapter)
	}

	this.updatePage = function(chapterNumber) {
		this.page = pageNumber;
		this.pageObject = this.series[this.chapter].pages[this.page];
		this.S.out('state_page', this.page)
	}
	
	this.S.mapIn({
		'series_data': this.storeSeries,
		'state_chapter': this.updateChapter,
		'state_page': this.updatePage
	})
	this.S.mapOut([
		'data',
		'state_chapter',
		'state_page'
	]);
}


function UI_Reader(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Reader'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this);

	this.store = o.store;
	this.SCP = {};
	
	this.keyListener =
		new KeyListener()
			.attach('prev', ['ArrowLeft'], e => Action.prevPage())
			.attach('next', ['ArrowRight'], e => Action.nextPage())
			.attach('prevCh', ['BracketLeft'], e => Action.prevChapter())
			.attach('nextCh', ['BracketRight'], e => Action.nextChapter())
			.attach('cycleFit', ['KeyF'], e => this.cycleFit())

	this.selector_chap = new UI_SimpleList({
		node: this._.selector_chap
	}).S.linkAnonymous('id', id => Action.displayChapter(id));
	this.selector_vol = new UI_SimpleList({
		node: this._.selector_vol
	}).S.linkAnonymous('id', id => Action.displayVolume(id));

	this.imageView = new UI_ReaderImageView({
		node: this._.image_viewer
	})

	this.drawReader = function() {
		this._.title.innerHTML = this.store.series.title;
	var chapterElements = [];
	var volElements = {};
		for(var i=0; i < this.store.series.chaptersIndex.length; i++) {
		var chapterNumber = this.store.series.chaptersIndex[i];
		var chapter = this.store.series.chapters[chapterNumber];
			chapterElements.push(new UI_SimpleListItem({
				text: chapterNumber + ' - ' + chapter.title,
				value: chapterNumber
			}));
			volElements[chapter.volume] = true;
		}
		volElements = Object.keys(volElements).sort((a,b) => parseFloat(b) - parseFloat(a)).map(item => {
			return new UI_SimpleListItem({
				value: item
			})
		});

		this.selector_chap.clear().add(chapterElements);
		this.selector_vol.clear().add(volElements);
	}

	this.drawChapter = function() {
		this.imageView.drawImages(this.store.series.chapters[this.SCP.chapter].images);
		this.selector_chap.$.value = this.SCP.chapter;
		this.selector_vol.$.value = this.store.series.chapters[this.SCP.chapter].volume;
		this.displayPage(0);
		return this;
	}

	this.displayPage = function(page) {
		if(page == 'last')
			page = this.SCP.chapterObject.images.length - 1;
		this.imageView.selectPage(page);
	}


	this.nextChapter = function(){
	var chapArr = Object.keys(this.store.series.chapters).sort((a,b) => parseFloat(a) - parseFloat(b))
		if(this.state.currentChapter < chapArr.length - 2)
			this.drawChapter(
				chapArr[chapArr.indexOf(this.state.currentChapter)+1]
			)
	}
	this.prevChapter = function() {
	var chapArr = Object.keys(this.store.series.chapters).sort((a,b) => parseFloat(a) - parseFloat(b))
		if(this.state.currentChapter > 1)
			this.drawChapter(
				chapArr[chapArr.indexOf(this.state.currentChapter) - 1]
			)
	}
	this.nextPage = function(){
		if(this.state.currentPage < this.store.series.chapters[this.state.currentChapter].pages.length - 1) 
			this.displayPage(this.state.currentPage + 1)
		else
			Action.nextChapter();
	}
	this.prevPage = function(){
		if(this.state.currentPage > 0) 
			this.displayPage(this.state.currentPage - 1)
		else {
			Action.prevChapter();
			Action.displayPage('last');
		}
	}

	this.cycleFit = function() {
	var fits = [
			'fit-width',
			'fit-height',
			'fit-none'
		];
		this.imageView.$.classList.cycle(fits);
		this._.fit_button.classList.cycle(fits);
	}

	this.cycleLayout = function() {
		switch(this.imageView.displayLayout) {
			case 'ltr':
			var newLayout = displayLayout = 'ttb';
				break;
			case 'ttb':
				newLayout = displayLayout ='rtl';
				break;
			case 'rtl':
				newLayout = displayLayout ='ltr';
				break;
		}
		this.$.classList.remove(this.imageView.displayLayout);
		this.$.classList.add(newLayout);
		this.imageView.displayLayout = newLayout;

		this.imageView.drawImages(this.store.series.chapters[this.state.currentChapter].images);
		this.imageView.selectPage(this.imageView.currentPage);
	}

	this._.chap_prev.onmousedown = e => Action.prevChapter(e);
	this._.chap_next.onmousedown = e => Action.nextChapter(e);
	this._.vol_prev.onmousedown = e => Action.prevVolume(e);
	this._.vol_next.onmousedown = e => Action.nextVolume(e);
	this._.fit_button.onmousedown = e => this.cycleFit(e);
	this._.layout_button.onmousedown = e => this.cycleLayout(e);

	this.S.mapIn({
		'series_data': this.updateData,
		'state_series': this.drawReader,
		'state_chapter': this.drawChapter,
		'state_page': this.displayPage,
	})
}

function UI_ReaderImageView(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['ReaderImageView'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.currentPage = 0;
	this.displayLayout = 'ltr';

	this.imageContainer = new UI_Tabs({node: this._.image_container})

	this.drawImages = function(images) {
		this.imageContainer.clear();
		images.forEach((url, index) => {
			this.imageContainer.add(new UI_WrappedImage({src: url, index: index}))
		})
		if(this.displayLayout == 'rtl') this.imageContainer.reverse();
	}

	this.selectPage = function(index) {
		if(index < 0 || index >= this.imageContainer.$.children.length)
			return;
	var pageElement = this.$.querySelector('*[data-index="'+index+'"]')
	var realIndex = this.imageContainer.$.children.indexOf(pageElement);
		this.imageContainer.select(realIndex);
		this.currentPage = index;
		if(this.displayLayout == 'ttb'){
			/*this.$.scrollTo({
				left: 0,
				top: pageElement.offsetTop
			})*/
		}else{
			this.imageContainer.$.style.textIndent = -1 * 100 * realIndex - 0.001 + '%';
			//setTimeout(() => scrollToY(this.$, 0, 0.15, 'easeInOutSine'), 150)
			// setTimeout(() => {
				this.imageContainer.selectedItems[0].$.style.top = 0;
				this.$.scrollTo({
					left: 0,
					top: 0
				})
			// }, 150)
		}
	}

	this.prev = function() {
		this.selectPage(this.currentPage - 1);

	}
	this.next = function() {
		this.selectPage(this.currentPage + 1);
	}


	this.$.onscroll = e => {
		if(this.displayLayout == 'ttb') {
		var offsets = this.imageContainer.$.children.map(item => item.offsetTop);
			offsets.push(this.$.scrollTop);
			offsets = offsets.sort((a, b) => a - b);
			Action.displayPage(offsets.indexOf(this.$.scrollTop) - 1);
			return;
		}
		if(this.imageContainer.selectedItems[0].$.nextSibling)
			this.imageContainer.selectedItems[0].$.nextSibling.style.top = this.$.scrollTop + 'px';
		if(this.imageContainer.selectedItems[0].$.prevSibling)
			this.imageContainer.selectedItems[0].$.prevSibling.style.top = this.$.scrollTop + 'px';
	}
	this.mouseHandler = function(e) {
	var box = this.$.getBoundingClientRect();
	var cutoff = box.width * 0.35 + box.left;
		if(e.pageX > cutoff) {
			(this.displayLayout == 'rtl')?
				Action.prevPage(e):
				Action.nextPage(e);
		}else if(e.pageX > box.left){
			(this.displayLayout == 'rtl')?
				Action.nextPage(e):
				Action.prevPage(e);
		}
	}

	this.$.onmousedown = e => this.mouseHandler(e);
}

function URLChanger(o) {
	o=be(o);
	Linkable.call(this);

	this.updateURL = function(SCP) {
		window.history.replaceState(
			{},
			SCP.seriesObject.title
				+ ' Chapter '
				+ SCP.chapter
				+ ', Page '
				+ (SCP.page + 1),
			"/reader/series/"
				+ SCP.seriesObject.slug
				+ '/'
				+ SCP.chapter.replace('.', '-')
				+ '/'
				+ (SCP.page + 1)
		);
	}

	this.S.mapIn({
		SCP: this.updateURL
	})
}

function UI_SimpleList(o) {
	o=be(o);
	UI_List.call(this, {
		node: o.node,
		kind: ['SimpleList'].concat(o.kind || []),
	});
	Linkable.call(this);

	this.handler = e => {
		this.S.out('id', this.$.value)
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

	this.S.mapOut(['id'])
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
		this.$.innerHTML = o.text || o.value || '<List Element>';
}

function UI_WrappedImage(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['WrappedImage'].concat(o.kind || []),
		html: o.html || '<div><img data-bind="image" src="" /></div>'
	});

	this._.image.src = o.src;
	this.$.setAttribute('data-index', o.index)
}

alg.createBin();

Action = new ActionHandler({
	url: '/api/',
	mediaURL: '/media/manga/'
});
ReaderStorage = new Reader_StorageHandler();
Reader = new UI_Reader({
	node: document.getElementById('rdr-main'),
	store: ReaderStorage
});
Loader = new LoadHandler();


Action.S.link(ReaderStorage);
ReaderStorage.S.link(Reader)