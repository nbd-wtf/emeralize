/**
 * HSTypedJS wrapper.
 *
 * @author Htmlstream
 * @version 3.0
 *
 */

HSCore.components.HSTyped = {
  dataAttributeName: 'data-hs-typed-options',
  defaults: {},

  collection: [],

  init(el, options, id) {
    const that = this;
    let elems;

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
      return false
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
        options
      )
    })
  },

  _init: function () {
    const that = this;

    for (let i = 0; i < that.collection.length; i += 1) {
      let _$el
      let _options

      if (that.collection[i].hasOwnProperty('$initializedEl')) {
        continue
      }

      _$el = that.collection[i].$el
      _options = that.collection[i].options

      that.collection[i].$initializedEl = new Typed(
        _$el,
        _options
      )
    }
  }
}
