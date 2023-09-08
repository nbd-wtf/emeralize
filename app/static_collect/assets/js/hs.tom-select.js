/*
* HSTomSelect Plugin
* @version: 1.0.0 (Mon, 24 May 2021)
* @requires: tom-select 1.7.26
* @author: HtmlStream
* @event-namespace: .HSTomSelect
* @license: Htmlstream Libraries (https://htmlstream.com/)
* Copyright 2021 Htmlstream
*/

HSCore.components.HSTomSelect = {
  dataAttributeName: 'data-hs-tom-select-options',
  defaults: {
    dropdownWrapperClass: 'tom-select-custom',
    searchInDropdown: true,
    plugins: [
      'change_listener',
      'hs_smart_position'
    ],
    hideSelected: false,
    render: {
      'option': function(data, escape) {
        return data.optionTemplate || `<div>${data.text}</div>>`
      },
      'item': function(data, escape) {
        return data.optionTemplate || `<div>${data.text}</div>>`
      }
    }
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
      let $clearBtn

      if (that.collection[i].hasOwnProperty('$initializedEl')) {
        continue
      }

      _options = that.collection[i].options
      _$el = that.collection[i].$el

      if (_options.plugins.hasOwnProperty('hs_smart_position') && !_$el.closest('.modal')) {
        _options.dropdownParent = 'body'
      }

      if (_$el.hasAttribute('multiple')) {
        _options.plugins = [..._options.plugins, 'remove_button']
      }

      if (_options.searchInDropdown) {
        _options.plugins = [..._options.plugins, 'dropdown_input']
      }

      TomSelect.define('hs_smart_position', function(plugin_options) {
        function smartPositionOnScroll(instance) {
          const menuBoundary = instance.$menu.getBoundingClientRect()
          if (menuBoundary.bottom > window.innerHeight) {
            instance.$menu.style.top = `${parseInt(instance.$menu.style.top) - (instance.control.clientHeight + instance.$menu.clientHeight + 10)}px`
          } else if (menuBoundary.top < 0) {
            instance.$menu.style.top = `${parseInt(instance.$menu.style.top) + (instance.control.clientHeight + instance.$menu.clientHeight + 10)}px`
          }
        }

        this.hook('after','setup',function (){
          this.$menu = this.dropdown_content.parentElement

          this.on('dropdown_open', $menu => {
            const menuBoundary = $menu.getBoundingClientRect(),
              wrapperBoundary = this.wrapper.getBoundingClientRect()
            if (menuBoundary.bottom > window.innerHeight) {
              $menu.style.top = `${parseInt($menu.style.top) - (this.control.clientHeight + $menu.clientHeight + 10)}px`
            }
            $menu.style.opacity = 0
            setTimeout(() => {
              const width = parseInt($menu.style.width)
              if (width > wrapperBoundary.width && _options.dropdownLeft) {
                $menu.style.left = `${parseInt($menu.style.left) - Math.abs((menuBoundary.width - width))}px`
              }
              $menu.style.opacity = 1
            })
          })
          window.addEventListener('scroll', () => smartPositionOnScroll(this))
        })
      })

      /* Start : Init */

      that.collection[i].$initializedEl = new TomSelect(
        _$el,
        _options
      )

      /* End : Init */

      if (_options.hideSearch) that.hideSearch(that.collection[i].$initializedEl, _options)
      if (_options.disableSearch) that.disableSearch(that.collection[i].$initializedEl, _options)
      if (_options.width) that.width(that.collection[i].$initializedEl, _options)
      if (_options.singleMultiple) that.singleMultiple(that.collection[i].$initializedEl, _options)
      if (_options.hidePlaceholderOnSearch) that.hidePlaceholderOnSearch(that.collection[i].$initializedEl, _options)
      if (_options.create) that.openIfEmpty(that.collection[i].$initializedEl, _options)
      if (_options.hideSelectedFromField) that.hideSelectedFromField(that.collection[i].$initializedEl, _options)
      if (_options.dropdownWidth) that.dropdownWidth(that.collection[i].$initializedEl, _options)

      that.renderPlaceholder(that.collection[i].$initializedEl, _options)
      that.wrapContainer(that.collection[i].$initializedEl, _options)
    }
  },

  hideSearch(tomSelect, settings) {
    tomSelect.control_input.parentElement.removeChild(tomSelect.control_input)
  },

  disableSearch(tomSelect, settings) {
    tomSelect.control_input.readOnly = true
  },

  singleMultiple(tomSelect, settings) {
    tomSelect.control.classList.add('hs-select-single-multiple')

    const defaultPlaceholder = (tomSelect.control_input.getAttribute('placeholder') || settings.placeholder).replace(/(<([^>]+)>)/gi, "")
    const handler = (e) => {
      if (e.target.closest('[data-selectable].selected')) {
        e.target.classList.remove('selected')
        setTimeout(() => {
          tomSelect.removeItem(e.target.getAttribute('data-value'), false)
          tomSelect.refreshItems()
        })
      }
    }
    const renderPlaceholder = (val) => {
      const $selectedCount = tomSelect.wrapper.querySelector('.ts-selected-count')

      if (!$selectedCount) {
        const $createSelectedCount = document.createElement('span')
        $createSelectedCount.classList.add('ts-selected-count')
        tomSelect.wrapper.querySelector('.items').appendChild($createSelectedCount)
      }

      return tomSelect.wrapper.querySelector('.ts-selected-count').innerHTML = val
    }

    if (tomSelect.items.length) {
      if (!settings.searchInDropdown) {
        tomSelect.control_input.setAttribute('placeholder', `${tomSelect.items.length} item(s) selected`)
      } else {
        renderPlaceholder(tomSelect.items.length ? `${tomSelect.items.length} item(s) selected` : defaultPlaceholder)
      }
    }

    tomSelect.on('dropdown_open', $menu => {
      $menu.addEventListener('mouseup', handler)
    })

    tomSelect.on('dropdown_close', $menu => {
      window.removeEventListener('mouseup', handler)
    })

    tomSelect.on('item_add', () => {
      if (tomSelect.items.length) {
        if (settings.searchInDropdown) {
          renderPlaceholder(`${tomSelect.items.length} item(s) selected`)
        } else {
          tomSelect.control_input.setAttribute('placeholder', `${tomSelect.items.length} item(s) selected`)
        }
      }
    })

    tomSelect.on('item_remove', () => {
      if (!tomSelect.items.length) {
        if (settings.searchInDropdown) {
          renderPlaceholder(defaultPlaceholder)
        } else {
          tomSelect.control_input.setAttribute('placeholder', defaultPlaceholder)
        }
      } else {
        if (settings.searchInDropdown) {
          renderPlaceholder(`${tomSelect.items.length} item(s) selected`)
        } else {
          tomSelect.control_input.setAttribute('placeholder', `${tomSelect.items.length} item(s) selected`)
        }
      }
    })
  },

  width(tomSelect, settings) {
    tomSelect.wrapper.style.maxWidth = settings.width
  },

  hidePlaceholderOnSearch(tomSelect, settings) {
    const defaultPlaceholder = (tomSelect.control_input.getAttribute('placeholder') || settings.placeholder).replace(/(<([^>]+)>)/gi, "")
    if (!defaultPlaceholder) return

    tomSelect.on('dropdown_open', () => {
      tomSelect.control_input.setAttribute('placeholder', '')
    })

    tomSelect.on('dropdown_close', () => {
      tomSelect.control_input.setAttribute('placeholder', defaultPlaceholder)
    })
  },

  openIfEmpty(tomSelect, settings) {
    tomSelect.control_input.addEventListener('focus', () => {
      if (tomSelect.$menu.querySelector('.option')) return
      tomSelect.open()
      setTimeout(() => {
        tomSelect.$menu.style.display = 'block'
        tomSelect.$menu.querySelector('.ts-dropdown-content').append(tomSelect.render('no_results'))
      }, 10)
    })
  },

  hideSelectedFromField(tomSelect, settings) {
    const onSelect = () => {
      console.log(tomSelect)
    }

    tomSelect.on('item_select', onSelect)
    tomSelect.on('item_add', onSelect)
  },

  dropdownWidth(tomSelect, settings) {
    tomSelect.on('dropdown_open', () => tomSelect.$menu.style.width = settings.dropdownWidth)
  },

  width(tomSelect, settings) {
    tomSelect.wrapper.style.width = settings.width
  },

  renderPlaceholder(tomSelect, settings) {
    if (settings.singleMultiple || tomSelect.items.length) return
    const defaultPlaceholder = tomSelect.input.getAttribute('placeholder') || settings.placeholder

    if (settings.searchInDropdown && !settings.hideSelected) {
      let placeholderElement = null
      const onSelect = function() {
        placeholderElement = tomSelect.wrapper.querySelector('.ts-custom-placeholder')
        if (tomSelect.items.length && placeholderElement) {
          if (placeholderElement.parentElement) {
            placeholderElement.parentElement.removeChild(placeholderElement)
          }
          return placeholderElement = null
        }

        if (!tomSelect.items.length && !placeholderElement) {
          addPlaceholder()
        }
      }
      const addPlaceholder = function() {
        if (tomSelect.items.length) return
        tomSelect.wrapper.querySelector('.items').innerHTML = `<span class="ts-custom-placeholder">${defaultPlaceholder}</span>`
        placeholderElement = tomSelect.wrapper.querySelector('.ts-custom-placeholder')
      }

      addPlaceholder()
      tomSelect.on('change', onSelect)
    }

    function addInputPlaceholder(defaultPlaceholder) {
      tomSelect.control_input.setAttribute('placeholder', defaultPlaceholder.replace(/(<([^>]+)>)/gi, ""))
    }

    function addTextPlaceholder(defaultPlaceholder) {
      const addPlaceholder = () => {
          tomSelect.control.innerHTML = `<div class="ts-custom-placeholder">${defaultPlaceholder}</div>`
        },
        removePlaceholder = () => {
          const $placeholder = tomSelect.wrapper.querySelector('.items .ts-custom-placeholder')
          if ($placeholder && $placeholder.parentElement) {
            $placeholder.parentElement.removeChild($placeholder)
          }
        }

      addPlaceholder()

      tomSelect.on('change', () => {
        if (tomSelect.items.length) {
          removePlaceholder()
        }

        if (!tomSelect.items.length) {
          addPlaceholder()
        }
      })
    }


    if (defaultPlaceholder) {
      if (tomSelect.control_input.offsetParent) {
        addInputPlaceholder(defaultPlaceholder)
      } else {
        addTextPlaceholder(defaultPlaceholder)
      }
    }
  },

  wrapContainer(tomSelect, settings) {
    var wrapper = document.createElement('div')
    wrapper.className += settings.dropdownWrapperClass
    tomSelect.$menu.parentNode.insertBefore(wrapper, tomSelect.$menu)
    wrapper.appendChild(tomSelect.$menu);
  }
}
