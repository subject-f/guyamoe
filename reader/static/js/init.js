var J = {
    	"id": "1",
        "title": "Kaguya-sama: Love is War",
        "chapters": {
            "139": {
                "volume": "14",
                "title": "Miyuki Shirogane wants to discuss",
                "pages": [
                    {
                        "type": "page",
                        "index": [
                            {
                                "x":104,
                                "y": 200,
                                "text": "THE CULTURE FESTIVAL IS OVER"
                            },
                        ],
                        "img_full": "//....../.../.../.jpg",
                        "img_100": "//....../.../.../.jpg",
                        "img_200": "//....../.../.../.jpg",
                        "img_blur": "//....../.../.../.jpg",
                    },
                    {
                        "type": "credits",
                        "img_full": "",
                        "img_100": "",
                        "img_200": "",
                        "img_blur": "",
                    }
                ]
            }
        }
    }

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
		this.S.out('action', {action: 'displaySCP', data: SCP});
	}

	document.body.onload = this.onload;

	this.S.mapOut(['action']);
}


function ActionHandler(o) {
	Linkable.call(this);

	this.displaySeries = function(slug) {
		this.S.out('action', {
			action: 'displaySeries',
			id: slug
		})
		return this;
	}
	this.displayChapter = function(id) {
		this.S.out('action', {
			action: 'displayChapter',
			id: id
		})
		return this;
	}
	this.displayPage = function(id) {
		this.S.out('action', {
			action: 'displayPage',
			id: id
		})
		return this;
	}
	this.displayVolume = function(id) {
		this.S.out('action', {
			action: 'displayVolume',
			id: id
		})
		return this;
	}
	this.displaySCP = function(SCP) {
		this.S.out('action', {
			action: 'displaySeries',
			id: SCP.series
		})
		this.S.out('action', {
			action: 'displayChapter',
			id: SCP.chapter
		})
		this.S.out('action', {
			action: 'displayPage',
			id: SCP.page
		})
		return this;
	}
	this.nextPage = function() {
		this.S.out('action', {
			action: 'nextPage'
		})
		return this;
	}
	this.prevPage = function() {
		this.S.out('action', {
			action: 'prevPage'
		})
		return this;
	}
	this.nextChapter = function() {
		this.S.out('action', {
			action: 'nextChapter'
		})
		return this;
	}
	this.prevChapter = function() {
		this.S.out('action', {
			action: 'prevChapter'
		})
		return this;
	}
	this.nextVolume = function() {
		this.S.out('action', {
			action: 'nextVolume'
		})
		return this;
	}
	this.prevVolume = function() {
		this.S.out('action', {
			action: 'prevVolume'
		})
		return this;
	}

	this.actionHandler = function(o) {
		this[o.action](o.data);
	}
	this.S.mapIn({action: this.actionHandler})
	this.S.mapOut(['action'])
}

function APIHandler(o) {
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

	this.actionHandler = function(o) {
		switch (o.action) {
			case 'displaySeries':
			this.seriesRequest = fetch(this.url + 'series/' + o.id)
					.then(response => response.json())
					.then(data => {
						this.S.out('data__series',
							this.infuseImageURLs(data)
						);
					}).then(() => {
						this.S.out('action', o);
					})
				break;
			case 'displayChapter':
			case 'displayPage':
				this.seriesRequest.then(() => {
					this.S.out('action', o);
				})
				break;
			default:
				this.S.out('action', o);
				break;
		}
		return this;
	}

	this.S.mapIn({
		action: this.actionHandler,
	})
	this.S.mapOut(['action', 'data__series'])
}

function StorageHandler(o) {
	o=be(o);
	Linkable.call(this);

	this.series = {};

	this.actionHandler = function(o) {
		this.S.out('action', o); //action passthrough
	}

	this.updateSeries = function(seriesObject) {
		this.series[seriesObject.slug] = seriesObject;
	}

	this.S.mapIn({
		action: this.actionHandler,
		data__series: d => this.updateSeries(d),
	});
	this.S.mapOut(['action', 'data__series']);
}


function UI_Reader(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Reader'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this);

	this.storage = o.storage;
	this.state = {
		currentSeries: null,
		currentPage: null,
		currentChapter: null,
		currentScroll: null
	};

	this.keyListener =
		new KeyListener()
			.attach('prev', ['ArrowLeft'], e => Action.prevPage())
			.attach('next', ['ArrowRight'], e => Action.nextPage())
			.attach('prevCh', ['BracketLeft'], e => Action.prevChapter())
			.attach('nextCh', ['BracketRight'], e => Action.nextChapter())

	this.selector_chap = new UI_SimpleList({
		node: this._.selector_chap
	}).S.linkAnonymous('id', id => Action.displayChapter(id));
	this.selector_vol = new UI_SimpleList({
		node: this._.selector_vol
	}).S.linkAnonymous('id', id => Action.displayVolume(id));

	this.imageView = new UI_ReaderImageView({
		node: this._.image_viewer
	})

	this.actionHandler = function(o) {
		switch (o.action) {
			case 'displaySeries':
				this.drawReader(o.id);
				break;
			case 'displayChapter':
				this.drawChapter(o.id)
				break;
			case 'displayPage':
				this.displayPage(o.id)
				break;
			case 'nextPage':
				this.nextPage();
				break;
			case 'prevPage':
				this.prevPage();
				break;
			case 'nextChapter':
				this.nextChapter();
				break;
			case 'prevChapter':
				this.prevChapter();
				break;
			default:
				break;
		}
	}

	this.drawReader = function(slug) {
		this.state.currentSeries = slug;
		this.seriesData = this.storage.series[this.state.currentSeries];

		this._.title.innerHTML = this.seriesData.title;

	var chapterElements = [];
	var volElements = {};
	var chapters = Object.keys(this.seriesData.chapters).sort((a,b) => parseFloat(b) - parseFloat(a));
		for(var i=0; i < chapters.length; i++) {
			var key = chapters[i];
			var chap = this.seriesData.chapters[key];
			chapterElements.push(new UI_SimpleListItem({
				text: key + ' - ' + chap.title,
				value: key
			}));
			volElements[chap.volume] = true;
		}
		volElements = Object.keys(volElements).sort((a,b) => parseFloat(b) - parseFloat(a)).map(item => {
			return new UI_SimpleListItem({
				value: item
			})
		});

		this.selector_chap.clear().add(chapterElements);
		this.selector_vol.clear().add(volElements);
	}

	this.drawChapter = function(chapter) {
		this.state.currentChapter = chapter;
		this.imageView.drawImages(this.seriesData.chapters[chapter].images);
		this.selector_chap.$.value = chapter;
		this.selector_vol.$.value = this.seriesData.chapters[chapter].volume;
		this.displayPage(0);
		return this;
	}

	this.nextChapter = function(){
	var chapArr = Object.keys(this.seriesData.chapters).sort((a,b) => parseFloat(a) - parseFloat(b))
		this.drawChapter(
				chapArr[chapArr.indexOf(this.state.currentChapter)+1]
			)
	}
	this.prevChapter = function(){
	var chapArr = Object.keys(this.seriesData.chapters).sort((a,b) => parseFloat(a) - parseFloat(b))
		this.drawChapter(
			chapArr[chapArr.indexOf(this.state.currentChapter) - 1]
		)
	}
	this.nextPage = function(){
		if(this.state.currentPage < this.seriesData.chapters[this.state.currentChapter].pages.length - 1) 
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

	this.displayPage = function(page) {
		if(page == 'last')
			page = this.seriesData.chapters[this.state.currentChapter].images.length - 1;
		this.imageView.selectPage(page);
		this.state.currentPage = page;
		window.history.replaceState(
			{},
			this.seriesData.title
				+ ' Chapter '
				+ this.state.currentChapter
				+ ', Page '
				+ (this.state.currentPage + 1),
			"https://kagu.algoinde.ru/reader/series/"
				+ this.seriesData.slug
				+ '/'
				+ this.state.currentChapter.replace('.', '-')
				+ '/'
				+ (this.state.currentPage + 1)
			);
	}

	this._.chap_prev.onmousedown = e => Action.prevChapter(e);
	this._.chap_next.onmousedown = e => Action.nextChapter(e);
	this._.vol_prev.onmousedown = e => Action.prevVolume(e);
	this._.vol_next.onmousedown = e => Action.nextVolume(e);

	this.S.mapIn({
		'action': this.actionHandler,
		'data__series': this.drawReader,
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

	this.imageContainer = new UI_Tabs({node: this._.image_container})

	this.drawImages = function(images) {
		this.imageContainer.clear();;
		images.forEach(url => {
			this.imageContainer.add(new UI_Image({src: url}))
		})
	}

	this.$.onscroll = e => {
		if(this.imageContainer.selectedItems[0].$.nextSibling)
			this.imageContainer.selectedItems[0].$.nextSibling.style.top = this.$.scrollTop + 'px';
		if(this.imageContainer.selectedItems[0].$.prevSibling)
			this.imageContainer.selectedItems[0].$.prevSibling.style.top = this.$.scrollTop + 'px';
	}

	this.selectPage = function(index) {
		if(index < 0 || index >= this.imageContainer.$.children.length)
			return;
		this.imageContainer.select(index);
		this.currentPage = index;
		this.imageContainer.$.style.textIndent = -1 * 100 * this.currentPage - 0.001 + '%';
		//setTimeout(() => scrollToY(this.$, 0, 0.15, 'easeInOutSine'), 150)
		setTimeout(() => {
			this.imageContainer.selectedItems[0].$.style.top = 0;
			this.$.scrollTo({
				left: 0,
				top: 0
			})
		}, 150)
	}

	this.prev = function() {
		this.selectPage(this.currentPage - 1);

	}
	this.next = function() {
		this.selectPage(this.currentPage + 1);
	}

	this.mouseHandler = function(e) {
	var box = this.$.getBoundingClientRect();
	var cutoff = box.width * 0.35 + box.left;
		if(e.pageX > cutoff) {
			Action.nextPage(e);
		}else if(e.pageX > box.left){
			Action.prevPage(e);
		}
	}

	this.$.onmousedown = e => this.mouseHandler(e);
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

function UI_Image(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Image'].concat(o.kind || []),
		html: o.html || '<img src="" />'
	});

	this.$.src = o.src;
}

alg.createBin();

API = new APIHandler({
	url: '/api/',
	mediaURL: '/media/manga/'
});
Storage = new StorageHandler();
Reader = new UI_Reader({
	node: document.getElementById('rdr-main'),
	storage: Storage
});
Action = new ActionHandler();
Loader = new LoadHandler();


Reader.S.link(API);
API.S.link(Storage);
Storage.S.link(Reader)
Action.S.link(API);
Loader.S.link(Action);
