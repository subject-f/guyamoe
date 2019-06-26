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


function APIHandler(o) {
	o=be(o);
	Linkable.call(this);
	this.url = o.url;
	this.mediaURL = '/media/manga/';

	this.infuseImageURLs = function(data) {
		for(var num in data.chapters) {
		var chapter = data.chapters[num];
			chapter.images = [];
			for (var i = 0; i < chapter.pagecount; i++) {
				chapter.images.push(this.mediaURL + data.slug + '/' + num + '/' + (chapter.pages[i]))
			}
		}
		return data;
	}

	this.request = function(requestObject) {
	var url;
		switch(requestObject.cmd) {
			case 'series':
	  		url = this.url + 'series/' + requestObject.id;
				break;
			default:
				console.error('Unhandled API request:', requestObject.cmd)
				break;
		}

		fetch(url)
			.then(response => {
				return response.json();
			})
			.then(data => {
				this.S.out('data__'+requestObject.cmd,
					this.infuseImageURLs(data)
				);
			})

		return this;
	}

	this.S.mapIn({request: this.request})
	this.S.mapOut(['data__pages', 'data__series'])
}

function StorageHandler(o) {
	o=be(o);
	Linkable.call(this);
	this.data = {};

	this.handle = function(type, data) {
		this.data[type] = data;
		this.S.out('data__'+type, this.data[type])
	}

	this.get = function(what) {
		return this.data[what];
	}

	this.S.mapIn({
		data__series: data => this.handle('series', data),
		data__pages: data => this.handle('pages', data) 
	});
	this.S.mapOut(['data__series', 'data__pages']);
} 

function UI_Reader(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Reader'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this);

	this.selector_chap = new UI_SimpleList({
		node: this._.selector_chap
	}).S.linkMapped(this, {'id': 'chapter'});
	this.selector_vol = new UI_SimpleList({
		node: this._.selector_vol
	}).S.linkMapped(this, {'id': 'volume'});

	this.imageView = new UI_ReaderImageView({
		node: this._.image_viewer
	})

	this.drawReader = function() {
		this._.title.innerHTML = Storage.get('series').title;

	var chapterElements = [];
	var volElements = {};
	var chapters = Object.keys(Storage.get('series').chapters).sort((a,b) => parseFloat(b) - parseFloat(a));
		for(var i=0; i < chapters.length; i++) {
			var key = chapters[i];
			var chap = Storage.get('series').chapters[key];
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

	this.initSeries = function(seriesID) {
		this.seriesID = seriesID;
		this.getSeries(seriesID);
		return this;
	}

	this.renderChapter = function(chapter) {
		this.imageView.renderChapter(chapter);
		return this;
	}

	this.getSeries = function(seriesID) {
		this.S.out('request', {'cmd': 'series', 'id': seriesID});
		return this;
	}

	this.S.mapIn({
		'data__series': this.drawReader,
		'series': this.initSeries,
		'chapter': this.renderChapter
	})
	this.S.mapOut(['request'])
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

	this.renderChapter = function(chapter) {
		this.imageContainer.clear();
	var images = Storage.get('series').chapters[chapter].images;
		images.forEach(url => {
			this.imageContainer.add(new UI_Image({src: url}))
		})
	}

	this.selectPage = function(index) {
		if(index < 0 || index >= this.imageContainer.$.children.length)
			return;
		this.imageContainer.select(index);
		this.currentPage = index;
		this.imageContainer.$.style.textIndent = -1 * 100 * this.currentPage + '%';
		this.$.scrollTo({
			left: this.imageContainer.selectedItems[0].$.offsetLeft,
			top: 0,
			behavior: 'smooth'
		})
	}

	this.prev = function() {
		this.selectPage(this.currentPage - 1);

	}
	this.next = function() {
		this.selectPage(this.currentPage + 1);
	}


	this._.page_next.onmousedown = e => this.next(e);
	this._.page_prev.onmousedown = e => this.prev(e);

	this.S.mapIn({
		url: this.renderChapter
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

API = new APIHandler({url: '/api/'});
Storage = new StorageHandler();
Reader = new UI_Reader({
	node: document.getElementById('rdr-main')
});

Reader.S.link(API);
API.S.link(Storage);
Storage.S.link(Reader)

Reader.initSeries('Kaguya-Wants-To-Be-Confessed-To');