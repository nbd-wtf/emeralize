/*
* Dropzone wrapper
* @version: 3.0.1 (Wed, 28 Jul 2021)
* @requires: dropzone v5.5.0
* @author: HtmlStream
* @event-namespace: .HSCore.components.HSDropzone
* @license: Htmlstream Libraries (https://htmlstream.com/licenses)
* Copyright 2021 Htmlstream
*/

HSCore.components.HSDropzone = {
  dataAttributeName: 'data-hs-dropzone-options',
  defaults: {
    // Default variables
    url: "index.html",
    thumbnailWidth: 300,
    thumbnailHeight: 300,
    previewTemplate: '<div class="col h-100 mb-4">' +
      '    <div class="dz-preview dz-file-preview">' +
      '      <div class="d-flex justify-content-end dz-close-icon">' +
      '        <small class="bi-x" data-dz-remove></small>' +
      '      </div>' +
      '      <div class="dz-details d-flex">' +
      '        <div class="dz-img flex-shrink-0">' +
      '         <img class="img-fluid dz-img-inner" data-dz-thumbnail>' +
      '        </div>' +
      '        <div class="dz-file-wrapper flex-grow-1">' +
      '         <h6 class="dz-filename">' +
      '          <span class="dz-title" data-dz-name></span>' +
      '         </h6>' +
      '         <div class="dz-size" data-dz-size></div>' +
      '        </div>' +
      '      </div>' +
      '      <div class="dz-progress progress">' +
      '        <div class="dz-upload progress-bar bg-success" role="progressbar" style="width: 0" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" data-dz-uploadprogress></div>' +
      '      </div>' +
      '      <div class="d-flex align-items-center">' +
      '        <div class="dz-success-mark">' +
      '          <span class="bi-check-lg"></span>' +
      '        </div>' +
      '        <div class="dz-error-mark">' +
      '          <span class="bi-x-lg"></span>' +
      '        </div>' +
      '        <div class="dz-error-message">' +
      '          <small data-dz-errormessage></small>' +
      '        </div>' +
      '      </div>' +
      '    </div>' +
      '</div>'
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

      that.collection[i].$initializedEl = new Dropzone(_$el, _options)

      /* End : Init */
    }
  }
}
