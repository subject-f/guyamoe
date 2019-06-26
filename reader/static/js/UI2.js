//Depends on:
//	alg_lib.0.3

var DEBUG = true;
const OFF = 0;
const ON = 1;
const TOGGLE = 2;


function KeyListener(target, mode) {
	this.target = target || document;
	this.listeners = {};
	this.pres = [];  
	this.conditions = [];
	this.exclusions = [];
	this.mode = mode || 'keydown';
	this.held = false;
	this.exclusiveness = false;
	if(!this.target._keyListener) {
		this.target._keyListener = {};
		this.target._keyListener.list = [];
		this.target._keyListener.hold = function(forwhat) {
			if(forwhat instanceof Array) {
				for(var i=0;i < this.list.length;i++) {
					if(forwhat.indexOf(this.list[i]) > -1) continue;
					this.list[i].hold();
				}	
			}else{
				for(var i=0;i < this.list.length;i++) {
					if(this.list[i] == forwhat) continue;
					this.list[i].hold();
				}
			}
			
		}
		this.target._keyListener.release = function() {
			for(var i=0;i < this.list.length;i++) {
				this.list[i].release();
			}
		}
	}
	this.target._keyListener.list.push(this);
	this.handler = e => {
		if(this.held) return;
		if(this.conditions.length > 0) {
			for(var i=0; i<this.conditions.length;i++) {
				if(this.conditions[i](e) === false) return;
			}
		}
		if(this.pres.length > 0) {
			this.pres.forEach(item => item(e))
		}
		if(this.exclusions.length > 0) {
			if(this.exclusions.indexOf(e.code) > -1) return;
		}
		for(var id in this.listeners) {
		var listener = this.listeners[id];
			if(!listener.held && (listener.keys == true ||
				listener.keys.indexOf(e.code) > -1) && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
				for(var i=0; i<listener.conditions.length;i++) {
					if(listener.conditions[i](e) === false) return;
				}
				e.stopPropagation();
				e.preventDefault();
				if(listener.callback) listener.callback(e);
				if(listener.exclusiveness) e.stopImmediatePropagation();
			}
		}
		if(this.exclusiveness) e.stopImmediatePropagation();
	}
	this.target.addEventListener(this.mode, this.handler, false);
}
KeyListener.prototype = {
	pre(f) {
		if(f) {
			this.pres.push(f);
		}
		return this;
	},
	condition(f, listenerID) {
		if(listenerID) {
			this.listeners[listenerID].conditions.push(f);
			return this;
		}
		if(f) {
			this.conditions.push(f);
		}
		return this;
	},
	exclude(f){
		if(f) {
			if(f instanceof KeyListener) {
				for(var id in f.listeners) {
				var extLst = f.listeners[id];
					this.exclude(extLst.keys)
				}
			}else if(f instanceof Array){
				this.exclusions.push.apply(this.exclusions, f);
			}
		}
		return this;
	},
	solo(state, listenerIDs) {
		if(listenerIDs) {
			if(typeof listenerIDs == 'string')
				listenerIDs = [listenerIDs];
			listenerIDs.forEach(listenerID => {
				switch(state) {
					case true:
					default:
						this.listeners[listenerID].exclusiveness = true;
						break;
					case false:
						this.listeners[listenerID].exclusiveness = false;
						break;
				}
			});
		}else{
			switch(state) {
				case true:
				default:
					this.exclusiveness = true;
					break;
				case false:
					this.exclusiveness = false;
					break;
			}
		}
		return this;
	},
	attach(id, keys, callback) {
		this.listeners[id] = {
			keys: keys,
			callback: callback,
			conditions: [],
			held: false
		};
		return this;
	},
	mirror(source, id) {
		if(id === true) {
			for(var id in source.listeners) {
			var extLst = source.listeners[id];
				this.attach(id, extLst.keys, extLst.callback)
			}
			return this;
		}
	var extLst = source.listeners[id];
		if(extLst) {
			this.attach(id, extLst.keys, extLst.callback);
		}
		return this;
	},
	hold(listenerID) {
		if(listenerID)
			this.listeners[listenerID].held = true;
		else
			this.held = true;
		return this;
	},
	release(listenerID) {
		if(listenerID)
			this.listeners[listenerID].held = false;
		else
			this.held = false;
		return this;
	},
	detach(id) {
	var listener = this.listeners[id];
		this.target.removeEventListener(this.mode, listener.handler);
		delete this.listeners[id];
		return this;
	},
	detachAll() {
		for(var id in this.listeners) {
		var listener = this.listeners[id];
			this.target.removeEventListener(this.mode, listener.handler);
			delete this.listeners[id];
		}
		return this;
	}
};



function UI(o) {
	
	/*
	Initialises an UI element. Creates or inherits a DOM node if specified.
	o {
		node: target dom element or wrapper
		callback: callback to execute (typically used on change, returns val)
	}
	*/

	this.init = function init(o) {
		o=be(o);
		this.me = {
			kind: ['UI'].concat(o.kind || []),
			node: o.node,
			html: o.html
		}
		if(DEBUG) console.log('Instancing UI_', this.me.kind, ': ', this);

		this.$ = this.me.node?this.me.node:this.conjure();
		this.$._struct = this;
		this.$.classList.add.apply(this.$.classList, this.me.kind);
		this._ = {};
	var binds = this.$.querySelectorAll('[data-bind]');
		binds.forEach(item => {
			this._[item.getAttribute('data-bind')] = item;
		})
		if(DEBUG)
			if(binds.length > 0)
				console.log('Binds added: ', Object.keys(this._), ': ', this);
		return o;
	}
	// Creates an element out of html template.
	this.conjure = function conjure() {
		if(!this.me.html) {
			throw 'CANNOT CONJURE: node and HTML is missing.'
			return false;
		}
		if(DEBUG) console.log('Node was not found. Creating an instance using embedded HTML tempate.')
	var holder = crelm();
		holder.innerHTML = this.me.html;
		return holder.firstElementChild;
	}

	this.init(o);

	//what?
	this.markers = {};
}


function Linkable(o) {
	o=be(o);
	this.S = {};
	this.S.outStreams = {};
	this.S.inStreams = {};
	this.S.outMappings = {};

	this.S.deadEnd = function(data) {console.log('Arrived at the dead end: ', data); return false};


	//Declare allowed input streams and their mappings to internal functions.
	//streams: {string: function}
	this.S.mapIn = streams => {
		for(let id in streams) {
			this.S.inStreams[id] = streams[id].bind(this) || this.S.deadEnd;
		}
		return this;
	}
	/* Example:
	this.S.mapIn({
		index: this.logger,
		number: this.adder
	})
	*/

	//Declares output stream names.
	//This creates empty arrays (for functions), because no external objects yet requested things to be outputted to them.
	//streamIDs: [streamID, streamID, ...]
	this.S.mapOut = streamIDs => {
		for (var i = 0; i < streamIDs.length; i++) {
			this.S.outStreams[streamIDs[i]] = [];
			this.S.outMappings[streamIDs[i]] = [];
		}
		return this;
	}

	this.S.addOut = streamID => {
		this.S.outStreams[streamID] = [];
		this.S.outMappings[streamID] = [];
	}

	this.S.delOut = streamID => {
		delete this.S.outStreams[streamID];	
		delete this.S.outMappings[streamID];	
	}

	this.S.addIn = (streamID, func) => {
		this.S.inStreams[streamID] = func.bind(this);
	}

	this.S.delIn = streamID => {
		delete this.S.inStreams[streamID];
	}

	/* Example:
	this.S.mapOut([
		number,
		element
	])
	*/

	this.S.link = (targetStructure, streamID) => {
		if(!targetStructure.S) {
			throw 'AlgEx: Target does not have stream support';
		}
		if(!streamID)
		var streamIDs = Object.keys(this.S.outStreams)
		else
			streamIDs = [streamID];

		for (var i = 0; i < streamIDs.length; i++) {
			if(!targetStructure.S.inStreams[streamIDs[i]])
				if(DEBUG) console.info('Target structure does not have input stream '+streamIDs[i]+' at the moment.')
			this.S.outStreams[streamIDs[i]].push(targetStructure);
			this.S.outMappings[streamIDs[i]].push({});
		}
		return this;
	}

	//{'source_stream_id': 'target_stream_id'}

	this.S.linkMapped =  (targetStructure, mapping) => {
		if(!targetStructure.S) {
			throw 'AlgEx: Target does not have stream support';
		}
		if(!mapping)
			throw 'AlgEx: No mapping supplied for mapped linking: ',this,'->',targetStructure;

		for (var sourceStream in mapping) {
		var targetStream = mapping[sourceStream];
			if(!targetStructure.S.inStreams[targetStream])
				if(DEBUG) console.info('Target structure does not have input stream '+targetStream+' at the moment.')
			this.S.outStreams[sourceStream].push(targetStructure);
			this.S.outMappings[sourceStream].push(mapping);
		}
		return this;
	}

	this.S.in = (streamID, data, sourceStructure) => {
		if(!this.S.inStreams[streamID]) {
			if(DEBUG) console.log(streamID,'does not exist in',this);
			return;
		}
		if(DEBUG) console.log(this,': Received',data,'from',sourceStructure,'on',streamID);
		this.S.inStreams[streamID](data);
	}

	this.S.out = (streamID, data) => {
	var targetStructures = this.S.outStreams[streamID];
	var targetMappings = this.S.outMappings[streamID];
		if(!targetStructures || targetStructures.length < 1) {
			if(DEBUG) console.warn('I have no outputs registered!', 'Tried to send', data, 'through', streamID)
			return this.S;
		}
		if(DEBUG) console.log('Sending',data, 'using stream '+streamID, '...');
		for (var i = 0; i < targetStructures.length; i++) {
			if (targetMappings && targetMappings.length > 0 && Object.keys(targetMappings[i]).length > 0) {
				targetStructures[i].S.in(targetMappings[i][streamID], data, this);
			}else{
				targetStructures[i].S.in(streamID, data, this);
			}
		}
		return this.S;
	}

	//Returns an input function for use in other objects by the stream index or alias.
	//This function is a map to an internal function of 'this' object.
	/*this.S.in = streamID => {
		return this.S.inStreams[streamID].bind(this);
	}*/

	//returns list of all input streams.
	/*this.S.getInputs = function(isNamed) {
	var numericalStreams = {};
	var namedStreams = {};
		for(var key in this.S.inStreams) {
			if(parseInt(key) > -1)
				numericalStreams[key] = this.S.inStreams[key];
			else
				namedStreams[key] = this.S.inStreams[key];
		}
		if(isNamed)
			return namedStreams;
		else
			return numericalStreams;
	}*/

	/*
	for(var key in this.S) {
	var declaration = this.S[key]
		if(typeof declaration == 'function') {
			this.S[key] = declaration.bind(this);
		}
	}*/
}

function UI_List(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['List'].concat(o.kind || []),
		html: o.html || '<ul></ul>',
	});
	this.lastAdded = [];

	for (var i = 0; i < this.$.children.length; i++) {
		if(!this.$.children[i]._struct) new UI_Dummy({node: this.$.children[i]})
	}

	this.get = function(index) {
		if (is(index))//errhandle
			if(is(this.$.children[index]))
				return this.$.children[index]._struct
			else
				throw 'AlgEx: Item index does not reference an item';
		else
			return this.$.children.reduce((keep, item) => keep.concat(item._struct), []);
	}

	this.add = function(uiInstance) {
		this.lastAdded = [];
		if(isList(uiInstance)){
			uiInstance.forEach(item => {
				this.$.appendChild(item.$);
				this.lastAdded.push(item);
			});
		}else{
			this.$.appendChild(uiInstance.$);
			this.lastAdded.push(uiInstance);
		}
		return this;
	}



	this.insertAt = function(uiInstance, referenceInstance) {
		//TD if child of $
		if(referenceInstance) return insertAfter(uiInstance.$, referenceInstance.$);
		else
			return; //errhandle
	}

	this.clear = function() {
		this.$.children.slice().forEach(item => alg.discardElement(item));
		this.lastAdded = [];
		return this;
	}

	this.renderAll = function() {
		this.$.children.slice().forEach(item => item._struct.render());
		return this;
	}

	this.consumeAll = function() {
		this.add(this.$.children.map(item => item._struct));
		return this;
	}
}


function UI_Dummy(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Dummy'].concat(o.kind || []),
		html: o.html || '<div></div>'
	});
	if(this.$.innerHTML.length < 1) this.$.innerHTML = o.text || '';
}

function UI_Separator(o) {
	o=be(o);
	UI_Dummy.call(this, {
		node: o.node,
		kind: ['Separator'].concat(o.kind || []),
		html: o.html || '<div></div>',
		text: o.text
	});

}


function UI_Selector(o) {
	o=be(o);
	UI_List.call(this, {
		node: o.node,
		kind: ['Selector'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this, {
		
	});
	this.singular = o.singular?true:false;
	this.persistent = o.persistent?true:false;
	this.toggleClass = o.toggleClass || 's';
	this.selectedItems = [];
	this.held = o.held||false;
	this.inverse = o.inverse||false;
	this.refire = o.refire||false;

	this.updateSelected = function()	{
		if(this.inverse)
			this.selectedItems = this.get().reduce((keep, item) => (item && !item.$.classList.contains(this.toggleClass))?keep.concat(item):keep, [])
		else
			this.selectedItems = this.get().reduce((keep, item) => (item && item.$.classList.contains(this.toggleClass))?keep.concat(item):keep, [])
		return this;
	}
	this.select = function(what, state, force) {
	var result = this.selectAbstract(what, state, force);
		return result;
	}

	this.selectAbstract = function(what, state, force) {
	var uiInstance;
		state = state || true;
		force = force || false;
		if(typeof what == 'number') {
			uiInstance = this.get(what)
		}else{
			uiInstance = what;
		}

		if(this.inverse) {
			if(this.singular) {
				switch(state) {
					case ON:
					default:
						if(!uiInstance.$.classList.contains(this.toggleClass) && force !== true)
							return;
						this.selectedItems.forEach(item => item.$.classList.add(this.toggleClass));
						uiInstance.$.classList.remove(this.toggleClass);
						break;
					case OFF:
						if(this.selectedItems.length < this.$.children.length && !uiInstance.$.classList.contains(this.toggleClass))
							return;
						uiInstance.$.classList.add(this.toggleClass);
						break;
					case TOGGLE:
						if(this.selectedItems.length < this.$.children.length && !uiInstance.$.classList.contains(this.toggleClass))
							return;
						this.selectedItems.forEach(item => item.$.classList.add(this.toggleClass));
						uiInstance.$.classList.toggle(this.toggleClass);
						break;
				}
			}else{
				switch(state) {
					case ON:
					default:
						uiInstance.$.classList.remove(this.toggleClass);
						break;
					case OFF:
						uiInstance.$.classList.add(this.toggleClass);
						break;
					case TOGGLE:
						uiInstance.$.classList.toggle(this.toggleClass);
						break;
				}
			}
			this.updateSelected()
		}else{
			if(this.singular) {
				switch(state) {
					case ON:
					default:
						if(uiInstance.$.classList.contains(this.toggleClass) && force !== true)
							return;
						this.selectedItems.forEach(item => item.$.classList.remove(this.toggleClass));
						uiInstance.$.classList.add(this.toggleClass);
						break;
					case OFF:
						if(this.selectedItems.length < 2 && uiInstance.$.classList.contains(this.toggleClass))
							return;
						uiInstance.$.classList.remove(this.toggleClass);
						break;
					case TOGGLE:
						if(this.selectedItems.length < 2 && uiInstance.$.classList.contains(this.toggleClass))
							return;
						this.selectedItems.forEach(item => item.$.classList.remove(this.toggleClass));
						uiInstance.$.classList.toggle(this.toggleClass);
						break;
				}
			}else{
				switch(state) {
					case ON:
					default:
						uiInstance.$.classList.add(this.toggleClass);
						break;
					case OFF:
						uiInstance.$.classList.remove(this.toggleClass);
						break;
					case TOGGLE:
						uiInstance.$.classList.toggle(this.toggleClass);
						break;
				}
			}
			this.updateSelected()
		}
		this.S.out('elements', this.selectedItems)
				.out('number', this.$.children.indexOf(uiInstance.$));
		return this.selectedItems;
	}
	
	this.handler = function(event) {
	var element;
		if(this.held) return;
		if(event.target !== this.$ && this.$.contains(event.target)) {
			element = event.target;
			do { 
			    if (element.parentNode == this.$) break;
			} while (element = element.parentNode);
			//errhandle if not a struct
			this.select(element._struct, TOGGLE);
		}
	}
	
	this.hold = function(state) {
		switch(state) {
			case ON:
			default:
				this.held = true;
				break;
			case OFF:
				this.held = false;
				break;
			case TOGGLE:
				this.held = !this.held;
				break;
		}
	}

	this.updateSelected();

	if(this.inverse) {
		for(var i=0;i < this.$.children.length;i++){
			if(!this.$.children[i].classList.contains(this.toggleClass)) {
				this.select(this.$.children[i]._struct, ON, true);
				if(this.singular) break;
			}else{
				this.select(this.$.children[i]._struct, OFF, true);
			}
		}
	}else{
		for(var i=0;i < this.$.children.length;i++){
			if(this.$.children[i].classList.contains(this.toggleClass)) {
				this.select(this.$.children[i]._struct, ON, true);
				if(this.singular) break;
			}
		}
	}

	this.$.onmousedown = e => this.handler(e);

	this.S.mapOut(['number','element']);

	return this;
}


function UI_ContainerList(o) {
	o=be(o);
	UI_Selector.call(this, {
		node: o.node,
		kind: ['ContainerList'].concat(o.kind || []),
		html: o.html || '<div></div>',
		toggleClass: 'is-hidden',
		held: true,
		persistent: true,
		singular: true,
		inverse: true,
	});
	Linkable.call(this);

	this.S.mapIn({
		number: this.select,
	})

}

function UI_ScrolledContainerList(o) {
	o=be(o);
	UI_ContainerList.call(this, {
		node: o.node,
		kind: ['ScrolledContainerList'].concat(o.kind || []),
		html: o.html || '<div></div>',
		refire: true
	});

	this.scrollSelect = function() {
		window.scrollTo({
			top: this.$.getBoundingClientRect().top + window.scrollY - 200,
			left: 0,
			behavior: 'smooth'
		});
		this.select.apply(this, arguments);
	}

	this.S.mapIn({
		number: this.scrollSelect,
	})
}



function UI_Tabs(o){
	o=be(o);
	UI_Selector.call(this, {
		node: o.node,
		kind: ['Tabs'].concat(o.kind || []),
		html: o.html || '<i></i>',
		singular: true,
		persistent: true,
		refire: true,
		toggleClass: 'is-active',
		held: o.held||false,
	});

	return this;
}

function UI_Input(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Input'].concat(o.kind || []),
		html: o.html || '<input type="text" />',
	});
	Linkable.call(this);

	if(o.placeholder) this.$.placeholder = o.placeholder;
	if(o.type) this.$.type = o.type;

	this.handler = function (e) {
		this.value = this.$.value;
		this.S.out('text', this.value);
	}
	this.clear = function () {
		this.value = this.$.value = '';
		this.S.out('text', this.value);
	}
	this.set = function(value, silent) {
		this.value = this.$.value = value;
		if(!silent) this.S.out('text', this.value);
	}

	this.keyl = new KeyListener(this.$)
			.attach('submit', ['Enter'], e => this.handler(e))
			.attach('cancel', ['Escape'], e => this.clear());

	map
}

function UI_Button(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Button'].concat(o.kind || []),
		html: o.html || '<div></div>',
	});
	Linkable.call(this);
	this.method = o.method || 'onclick';
	this.functions = o.functions || {};
	this.data = o.datas || {};

	if(this.$.innerHTML.length < 1) this.$.innerHTML = o.text || 'Button';

	
	this.set = function(name, func, data) {
		this.functions[name] = func.bind(this);
		this.data[name] = data;
		this.S.addOut(name);
		this.S.addIn(name, func);
		return this;
	},
	this.remove = function(name) {
		delete this.functions[name];
		this.S.delOut(name);
		return this;
	}

	this.trigger = function trigger(eventObject) {
		this.S.out('event', eventObject)
		for(var fn in this.functions) {
			this.functions[fn](this.data[fn], eventObject);
			this.S.out(fn, this.data[fn])
		}
		return this;
	}

	this.S.mapOut(['event']);

	this.$[this.method] = event => this.trigger(event);
}


function DataElement(o) {
	o=be(o);

	this.setData = function(data) {
		this.data = data;
	}
	this.getData = function() {
		return this.data;
	}

	this.setData(be(o.data));
}


function UI_Editable(o) {
	o=be(o);
	Object.assign(o,{
		node: o.node,
		kind: ['Editable'].concat(o.kind || []),
		html: o.html || '<div></div>',
		functions: o.functions
	});
	UI_Button.call(this, o)
	UI_Waitable.call(this);

	this.$.onkeydown = (e) => this.filterNewlines(e);
	this.$.oninput = (e) => this.filterTags(e);
	this.keyl = new KeyListener(this.$)
			.condition(e => {
				return this.renaming;
			})
			.pre(e => this.filterNewlines(e))
			.attach('submit', ['Enter'], e => this.confirm(e))
			.attach('cancel', ['Escape'], e => this.exit());


	this.filterNewlines = function filterNewlines(e) {
	    if(e.which == 13) {
			e.preventDefault();
			return false;
		}
		this.filterTags();
	}
	this.filterTags = function filterTags(e) {
	    for(var i=0; i<this.$.children.length; i++) {
    		this.$.children[0].parentNode.removeChild(this.$.children[0]);
	    };
	    if(this.$.innerHTML.length < 1)
	    	this.$.innerHTML='<br>';
	}

	this.edit = function edit(state) {
		switch(state) {
			case ON:
			default:
				this.editing = true;
				break;
			case OFF:
				this.editing = false;
				break;
			case TOGGLE:
				this.editing = !this.editing;
				break;
		}
		if(this.editing) {
			this.$.classList.add('edit');
			this.$.contentEditable = true;
		}else{
			this.$.classList.remove('edit');
			this.$.contentEditable = false;
		}
	}

	this.getText = function getText() {
		return this.$.innerHTML.replace(/\<br\>/g, '');
	}

	this.confirm = function confirm(e) {
		this.edit(false);
		this.trigger({struct:this, action:'confirm', text: this.getText()}, e)
	}

	this.cancel = function cancel(e) {
		this.edit(false);
		this.trigger({struct:this, action:'cancel'}, e)
	}
}

function UI_Waitable(o) {
	o=be(o);
	this.startWait = function startWait() {
		this.$.classList.add('w');
	}
	this.endWait = function endWait() {
		this.$.classList.remove('w');
	}
}

function UI_Slider(o) {
	o=be(o);
	UI.call(this, {
		node: o.node,
		kind: ['Slider'].concat(o.kind || []),
		html: o.html || '<div class="slider"><div class="prev"></div><div class="wrapper"></div><div class="next"></div></div>',
	});
	Linkable.call(this, {});

	this._ = {
		items: this.$.querySelector('.wrapper'),
		prev: this.$.querySelector('.prev'),
		next: this.$.querySelector('.next')
	}

	this.items = new UI_Selector({node: this._.items, singular: true, persistent: true, toggleClass: 's', held: true});

	this.move = function move(direction) {
		if(direction == 'left') {
			this._.items.insertBefore(this._.items.lastElementChild, this._.items.firstElementChild);
			this.items.select(this._.items.children.indexOf(this.items.selectedItems[0].$)-1);
		}else if(direction == 'right') {
			this._.items.appendChild(this._.items.firstElementChild);
			this.items.select(this._.items.children.indexOf(this.items.selectedItems[0].$)+1);
		}
	}

	this._.prev.onclick = () => this.move('left');
	this._.next.onclick = () => this.move('right');
}


Util = {}

Util.parseVKTags = function(text) {
var matches = /\[([a-zA-Z0-9_]+)\|(.+)\]/g.exec(text);
	if(matches != null) {
		return text.replace(matches[0], '<a href="https://vk.com/'+matches[1]+'">'+matches[2]+'</a>')
	}else{
		return text;
	}
}

var UIs = document.querySelectorAll('*[data-ui]');
var toUI = [];
UIs.forEach(node => {
	toUI.push({node: node, depth: alg.getDepth(node)})
});
toUI.sort((a,b) => {
	return a.depth>b.depth?1:-1;
})
toUI.forEach(item => {
	new window[item.node.getAttribute('data-ui')]({node: item.node})
});