  /*  * Circles wrapper
  * @version: 2.0.0 (Mon, 25 Nov 2019)
  * @requires: jQuery v3.0 or later, circles v0.0.6, appear.js v1.0.3
  * @author: HtmlStream
  * @event-namespace: .HSCore.components.HSCircles
  * @license: Htmlstream Libraries (https://htmlstream.com/licenses)
  * Copyright 2020 Htmlstream
  */

  HSCore.components.HSCircles = {
    dataAttributeName: 'data-hs-circles-options',
    defaults: {
      radius: 80,
      duration: 1000,
      wrpClass: 'circles-wrap',
      colors: ["#3170e5", "#e7eaf3"],
      bounds: -100,
      debounce: 10,
      rtl: false,
      isHideValue: false,
      dividerSpace: null,
      isViewportInit: false,
      fgStrokeLinecap: null,
      fgStrokeMiterlimit: null,
      additionalTextType: null,
      additionalText: null,
      textFontSize: null,
      textFontWeight: null,
      textColor: null,
      secondaryText: null,
      secondaryTextFontWeight: null,
      secondaryTextFontSize: null,
      secondaryTextColor: null
    },

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

    // ----- Start : Preparation -----
    setId: function($el, settings) {
      $el.setAttribute('id', settings.id)
    },
    // ----- End : Preparation -----

    // ----- Start : Custom functionality -----
    setTextStyles: function ($el, settings, initEl) {
      $el.querySelectorAll('[class="' + (settings.textClass || initEl._textClass) + '"]')
        .forEach(item => {
          item.style.fontSize = `${settings.textFontSize}px`
          item.style.fontWeight = settings.textFontWeight
          item.style.color = settings.textColor
          item.style.lineHeight = 'normal'
          item.style.height = 'auto'
          item.style.top = ''
          item.style.left = ''
        })
    },

    setRtl: function($el, settings) {
      $el.querySelectorAll('svg').forEach(item => {
        item.style.transform = 'transform', 'matrix(-1, 0, 0, 1, 0, 0)'
      })
    },

    setStrokeLineCap: function($el, settings, initEl) {
      $el.querySelectorAll('[class="' + initEl._valClass + '"]').forEach(item => {
        item.setAttribute('stroke-linecap', settings.fgStrokeLinecap)
      })
    },

    setStrokeMiterLimit: function($el, settings, initEl) {
      $el.querySelectorAll('[class="' + initEl._valClass + '"]').forEach(item => {
        item.setAttribute('stroke-miterlimit', settings.fgStrokeMiterlimit)
      })
    },

    initAppear: function($el, settings, initEl, params) {
      appear({
        bounds: settings.bounds,
        debounce: settings.debounce,
        elements: () => {
          return document.querySelectorAll('#' + settings.id)
        },
        appear: function (el) {
          initEl.update(JSON.parse(el.getAttribute('data-hs-circles-options')).value)
        }
      })
    },

    addToCollection(item, options, id) {
      const that = this

      const tempOptions = Object.assign(
        {},
        that.defaults,
        item.hasAttribute(that.dataAttributeName)
          ? JSON.parse(item.getAttribute(that.dataAttributeName))
          : {},
        options,
      )

      this.collection.push({
        $el: item,
        options: Object.assign({},  {
          id: "circle-" + Math.random().toString().slice(2),
          value: 0,
          text: function (value) {
            if (tempOptions.type === 'iconic') {
              return tempOptions.icon;
            } else {
              if (tempOptions.additionalTextType === 'prefix') {
                if (tempOptions.secondaryText) {
                  return (tempOptions.additionalText || "") + (tempOptions.isHideValue ? "" : value) + '<div style="margin-top: ' + (tempOptions.dividerSpace / 2 + 'px' || '0') + '; margin-bottom: ' + (tempOptions.dividerSpace / 2 + 'px' || '0') + ';"></div>' + '<div style="font-weight: ' + tempOptions.secondaryTextFontWeight + '; font-size: ' + tempOptions.secondaryTextFontSize + 'px; color: ' + tempOptions.secondaryTextColor + ';">' + tempOptions.secondaryText + '</div>';
                } else {
                  return (tempOptions.additionalText || "") + (tempOptions.isHideValue ? "" : value)
                }
              } else {
                if (tempOptions.secondaryText) {
                  return (tempOptions.isHideValue ? "" : value) + (tempOptions.additionalText || "") + '<div style="margin-top: ' + (tempOptions.dividerSpace / 2 + 'px' || '0') + '; margin-bottom: ' + (tempOptions.dividerSpace / 2 + 'px' || '0') + ';"></div>' + '<div style="font-weight: ' + tempOptions.secondaryTextFontWeight + '; font-size: ' + tempOptions.secondaryTextFontSize + 'px; color: ' + tempOptions.secondaryTextColor + ';">' + tempOptions.secondaryText + '</div>';
                } else {
                  return (tempOptions.isHideValue ? "" : value) + (tempOptions.additionalText || "")
                }
              }
            }
          }
        }, tempOptions),
        id: id || null
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

        if (_options.isViewportInit) {
          _options.value = 0;
        }

        /* Start : object preparation */

        that.setId(_$el, _options)

        /* End : object preparation */

        that.collection[i].$initializedEl = Circles.create(_options)

        /* Start : custom functionality implementation */

        that.setTextStyles(_$el, _options, that.collection[i].$initializedEl)

        if (_options.rtl) {
          that.setRtl(_$el, _options)
        }

        if (_options.fgStrokeLinecap) {
          that.setStrokeLineCap(_$el, _options, that.collection[i].$initializedEl)
        }

        if (_options.fgStrokeMiterlimit) {
          that.setStrokeMiterLimit(_$el, _options, that.collection[i].$initializedEl)
        }

        if (_options.isViewportInit) {
          that.initAppear(_$el, _options, that.collection[i].$initializedEl)
        }

        /* End : Init */
      }
    }
  }
