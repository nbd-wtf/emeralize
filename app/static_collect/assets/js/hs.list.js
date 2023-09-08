/**
 * List JS wrapper.
 *
 * @author Htmlstream
 * @version 2.0
 *
 */


HSCore.components.HSList = {
  dataAttributeName: 'data-hs-list-options',
  defaults: {
    searchMenu: false,
    searchMenuDelay: 300,
    searchMenuOutsideClose: true,
    searchMenuInsideClose: true,
    clearSearchInput: true,
    keyboard: false,
    empty: false
  },
  collection: [],

  init: function (el, options, id) {
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

    return this
  },

  initializeHover: function ($el, settings, newList) {
    const that = this
    var searchFiled = $el.querySelector(`.${newList.searchClass}`),
      selected = false

    /* Start : Keboard Support */
    searchFiled.addEventListener('keydown', e => {
      if (e.which === 40) {
        e.preventDefault()

        that.searchMenuShow($el, settings, newList)

        var activeItem = newList.list.querySelector('.active')

        if (!activeItem) {
          selected = newList.list.firstChild
          selected.classList.add('active')
        } else {
          if (activeItem.nextElementSibling) {
            var newActive = activeItem.nextElementSibling
            newActive.classList.add('active')
            selected.classList.remove('active')
            selected = newActive

            if (newList.list.offsetHeight < newActive.getBoundingClientRect().top) {
              newList.list.scrollTop = newActive.getBoundingClientRect().top + newList.list.scrollTop
            }
          }
        }
      } else if (e.which === 38) {
        e.preventDefault()

        var activeItem = newList.list.querySelector('.active')

        if (!activeItem) {
          selected = newList.list.firstChild.parentNode
          selected.classList.add('active')
        } else {
          if (activeItem.previousElementSibling) {
            var newActive = activeItem.previousElementSibling
            newActive.classList.add('active')
            selected.classList.remove('active')
            selected = newActive

            if (0 > newActive.getBoundingClientRect().top) {
              newList.list.scrollTop = newActive.getBoundingClientRect().top + newList.list.scrollTop - newList.list.offsetHeight
            }
          }
        }
      } else if (e.which == 13 && searchFiled.value.length > 0) {
        e.preventDefault()

        const href = selected.querySelector('a').getAttribute('href')
        if (href) {
          window.location = href
        }
      }
    })
  },

  searchMenu: function ($el, settings, newList) {
    const that = this
    if ($el.querySelector(`.${newList.searchClass}`).value.length === 0 || newList.visibleItems.length === 0 && !settings.empty) {
      that.helpers.fadeOut(newList.list, settings.searchMenuDelay)
      return that.helpers.hide(settings.empty)
    }

    that.searchMenuShow($el, settings, newList)
  },

  searchMenuShow: function ($el, settings, newList) {
    const that = this

    that.helpers.fadeIn(newList.list, settings.searchMenuDelay)

    if (!newList.visibleItems.length) {
      var empty = that.helpers.show(document.querySelector(settings.empty).cloneNode(true))
      newList.list.innerHTML = empty.outerHTML
    }
  },

  searchMenuHide: function ($el, settings, newList) {
    const that = this
    var searchFiled = $el.querySelector(`.${newList.searchClass}`)

    if (settings.searchMenuOutsideClose) {
      document.addEventListener('click', () => {
        that.helpers.fadeOut(newList.list, settings.searchMenuDelay)

        if (settings.clearSearchInput) {
          searchFiled.value = ''
        }
      })
    }

    if (!settings.searchMenuInsideClose) {
      newList.list.addEventListener('click', event => {
        event.stopPropagation()

        if (settings.clearSearchInput) {
          searchFiled.val('')
        }
      })
    }
  },

  emptyBlock: function ($el, settings, newList) {
    const that = this

    if ($el.querySelector(`.${newList.searchClass}`).value.length === 0 || newList.visibleItems.length === 0 && !settings.empty) {
      that.helpers.hide(settings.empty)
    } else {
      that.helpers.fadeIn(newList.list, settings.searchMenuDelay)

      if (!newList.visibleItems.length) {
        var empty = document.querySelector(settings.empty).clone()
        that.helpers.show(empty)
        newList.list.innerHTML = empty.outerHTML
      }
    }
  },

  // Helpers functions
  helpers: {
    fadeIn: (el, time) => {
      if (!el || el.offsetParent !== null) return el
      el.style.opacity = 0
      el.style.display = 'block'

      var last = +new Date()
      var tick = function () {
        el.style.opacity = +el.style.opacity + (new Date() - last) / time
        last = +new Date()

        if (+el.style.opacity < 1) {
          (window.requestAnimationFrame && requestAnimationFrame(tick)) || setTimeout(tick, 16)
        }
      }

      tick()
    },

    fadeOut: (el, time) => {
      if (!el || el.offsetParent === null) return el

      if (!time) {
        return el.style.display = 'none'
      }

      var intervalID = setInterval(function () {

        if (!el.style.opacity) {
          el.style.opacity = 1
        }

        if (el.style.opacity > 0) {
          el.style.opacity -= 0.1
        } else {
          clearInterval(intervalID)
          el.style.display = 'none'
        }

      }, time / 10)
    },

    hide: el => {
      el = typeof el === 'object' ? el : document.querySelector(el)
      el ? el.style.display = 'none' : el
      return el
    },

    show: el => {
      el = typeof el === 'object' ? el : document.querySelector(el)
      el ? el.style.display = 'block' : el
      return el
    }
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
    })
  },

  _init() {
    const that = this;

    for (let i = 0; i < that.collection.length; i += 1) {
      let _$el
      let _options

      if (that.collection[i].hasOwnProperty('$initializedEl')) {
        continue
      }

      _$el = that.collection[i].$el;
      _options = that.collection[i].options

      that.collection[i].$initializedEl = new List(
        _$el,
        _options,
        _options.values
      )

      if (_options.searchMenu) {
        that.helpers.hide(that.collection[i].$initializedEl.list)
      }

      that.collection[i].$initializedEl.on('searchComplete', () => {
        if (_options.searchMenu) {
          that.searchMenu(_$el, _options, that.collection[i].$initializedEl)
          that.searchMenuHide(_$el, _options, that.collection[i].$initializedEl)
        }

        if (!_options.searchMenu && _options.empty) {
          that.emptyBlock(_$el, _options, that.collection[i].$initializedEl)
        }
      })

      if (_options.searchMenu && _options.keyboard) {
        that.initializeHover(_$el, _options, that.collection[i].$initializedEl)
      }
    }
  },

  getItem(item) {
    if (typeof item === 'number') {
      return this.collection[item].$initializedEl;
    } else {
      return this.collection.find(el => {
        return el.id === item;
      }).$initializedEl;
    }
  }
}
