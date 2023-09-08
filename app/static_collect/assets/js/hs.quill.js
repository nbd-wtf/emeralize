/*
* Quill wrapper
* @version: 2.0.0 (Wed, 28 Jul 2021)
* @requires: quill v1.3.7
* @author: HtmlStream
* @event-namespace: .HSCore.components.HSQuill
* @license: Htmlstream Libraries (https://htmlstream.com/licenses)
* Copyright 2021 Htmlstream
*/


HSCore.components.HSQuill = {
  dataAttributeName: 'data-hs-quill-options',
  defaults: {
    theme: 'snow',
    attach: false
  },
  collection: [],

  init(el, options, id) {
    const that = this
    let elems

    if (el instanceof HTMLElement) {
      elems = [el]
    } else if (el instanceof Object) {
      elems = el
    } else {
      elems = document.querySelectorAll(el)
    }

    for (let i = 0; i < elems.length; i += 1) {
      that.addToCollection(elems[i], options, id || elems[i].id)
    }

    if (!that.collection.length) {
      return false;
    }

    // initialization calls
    that._init()
  },

  addToCollection(item, options, id) {
    const that = this

    this.collection.push({
      $el: item,
      id: id || null,
      options: Object.assign(
        {},
        that.defaults,
        item.hasAttribute(that.dataAttributeName)
          ? JSON.parse(item.getAttribute(that.dataAttributeName))
          : {},
        options,
      ),
    });
  },

  getItems() {
    const that = this;
    let newCollection = [];

    for (let i = 0; i < that.collection.length; i += 1) {
      newCollection.push(that.collection[i].$initializedEl);
    }

    return newCollection;
  },

  getItem(item) {
    if (typeof item === 'number') {
      return this.collection[item].$initializedEl;
    } else {
      return this.collection.find(el => {
        return el.id === item;
      }).$initializedEl;
    }
  },

  _init() {
    const that = this

    for (let i = 0; i < that.collection.length; i += 1) {
      let _options
      let _$el

      if (that.collection[i].hasOwnProperty('$initializedEl')) {
        continue;
      }

      _options = that.collection[i].options
      _$el = that.collection[i].$el

      /* Start : Init */

      that.collection[i].$initializedEl = new Quill(_$el, _options)

      _$el.classList.add('hs-quill-initialized')

      this.toolbarBottom(_options, that.collection[i].$initializedEl)

      /* End : Init */
    }
  },

  toolbarBottom: function (settings, newQuill) {
    if (settings.toolbarBottom) {
      const container = newQuill.container,
        toolbar = container.previousElementSibling,
        parent = container.parentElement

      parent.classList.add('ql-toolbar-bottom')

      if (settings.attach) {
        const attach = document.querySelector(settings.attach)
        attach.addEventListener('shown.bs.modal', () => {
          container.style.paddingBottom = toolbar.offsetHeight + 'px'
        })
      } else {
        container.style.paddingBottom = toolbar.offsetHeight + 'px'
      }

      toolbar.style.position = 'absolute'
      toolbar.style.width = '100%'
      toolbar.style.bottom = 0
    }
  }
}
