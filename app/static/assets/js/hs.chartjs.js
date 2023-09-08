/*
* Chart.js wrapper
* @version: 3.0.0 (Mon, 25 Nov 2021)
* @requires: Chart.js v2.8.0
* @author: HtmlStream
* @event-namespace: .HSCore.components.HSValidation
* @license: Htmlstream Libraries (https://htmlstream.com/licenses)
* Copyright 2021 Htmlstream
*/

function isObject(item) {
	return (item && typeof item === 'object' && !Array.isArray(item));
}

function mergeDeep(target, ...sources) {
	if (!sources.length) return target;
	const source = sources.shift();

	if (isObject(target) && isObject(source)) {
		for (const key in source) {
			if (isObject(source[key])) {
				if (!target[key]) Object.assign(target, { [key]: {} });
				mergeDeep(target[key], source[key]);
			} else {
				Object.assign(target, { [key]: source[key] });
			}
		}
	}

	return mergeDeep(target, ...sources);
}

HSCore.components.HSChartJS = {
	init: function (el, options) {
		this.$el = typeof el === "string" ? document.querySelector(el) : el
		if (!this.$el) return

		this.defaults = {
			options: {
				responsive: true,
				maintainAspectRatio: false,
				legend: {
					display: false
				},
				tooltips: {
					enabled: false,
					mode: 'nearest',
					prefix: '',
					postfix: '',
					hasIndicator: false,
					indicatorWidth: '8px',
					indicatorHeight: '8px',
					transition: '0.2s',
					lineWithLineColor: null,
					yearStamp: true
				},
				gradientPosition: {
					x0: 0,
					y0: 0,
					x1: 0,
					y1: 0,
				}
			}
		}
		var dataSettings = this.$el.hasAttribute('data-hs-chartjs-options') ? JSON.parse(this.$el.getAttribute('data-hs-chartjs-options')) : {}

		this.settings = mergeDeep(this.defaults, {...options, ...dataSettings},  ((dataSettings.type === 'bar') ? ({
			options: {
				scales: {
					yAxes: [{
						ticks: {
							callback: function (value, index, values) {
								var metric = settings.options.scales.yAxes[0].ticks.metric,
									prefix = settings.options.scales.yAxes[0].ticks.prefix,
									postfix = settings.options.scales.yAxes[0].ticks.postfix;

								if (metric && value > 100) {
									if (value < 1000000) {
										value = value / 1000 + 'k';
									} else {
										value = value / 1000000 + 'kk';
									}
								}

								if (prefix && postfix) {
									return prefix + value + postfix;
								} else if (prefix) {
									return prefix + value;
								} else if (postfix) {
									return value + postfix;
								} else {
									return value;
								}
							}
						}
					}]
				}
			}
		}) : ({})))

		this.settings = mergeDeep(this.settings, {
			options: {
				tooltips: {
					custom: function (tooltipModel) {
						// Tooltip Element
						var tooltipEl = document.getElementById('chartjsTooltip');

						// Create element on first render
						if (!tooltipEl) {
							tooltipEl = document.createElement('div');
							tooltipEl.id = 'chartjsTooltip';
							tooltipEl.style.opacity = 0;
							tooltipEl.classList.add('hs-chartjs-tooltip-wrap');
							tooltipEl.innerHTML = '<div class="hs-chartjs-tooltip"></div>';
							if (settings.options.tooltips.lineMode) {
								el.closest('.chartjs-custom').innerHTML = tooltipEl
							} else {
								document.body.appendChild(tooltipEl);
							}
						}

						// Hide if no tooltip
						if (tooltipModel.opacity === 0) {
							tooltipEl.style.opacity = 0;

							tooltipEl.parentNode.removeChild(tooltipEl)

							return;
						}

						// Set caret Position
						tooltipEl.classList.remove('above', 'below', 'no-transform');
						if (tooltipModel.yAlign) {
							tooltipEl.classList.add(tooltipModel.yAlign);
						} else {
							tooltipEl.classList.add('no-transform');
						}

						function getBody(bodyItem) {
							return bodyItem.lines;
						}

						// Set Text
						if (tooltipModel.body) {
							var titleLines = tooltipModel.title || [],
								bodyLines = tooltipModel.body.map(getBody),
								today = new Date();

							var innerHtml = '<header class="hs-chartjs-tooltip-header">';

							titleLines.forEach(function (title) {
								innerHtml += settings.options.tooltips.yearStamp ? title +  ', ' + today.getFullYear() : title;
							});

							innerHtml += '</header><div class="hs-chartjs-tooltip-body">';

							bodyLines.forEach(function (body, i) {
								innerHtml += '<div>'

								var oldBody = body[0],
									newBody = oldBody,
									color = tooltipModel.labelColors[i].backgroundColor instanceof Object ? tooltipModel.labelColors[i].borderColor : tooltipModel.labelColors[i].backgroundColor;

								innerHtml += (settings.options.tooltips.hasIndicator ? '<span class="d-inline-block rounded-circle mr-1" style="width: ' + settings.options.tooltips.indicatorWidth + '; height: ' + settings.options.tooltips.indicatorHeight + '; background-color: ' + color + '"></span>' : '') + settings.options.tooltips.prefix + (oldBody.length > 3 ? newBody : body) + settings.options.tooltips.postfix;

								innerHtml += '</div>'
							});

							innerHtml += '</div>';

							var tooltipRoot = tooltipEl.querySelector('.hs-chartjs-tooltip');
							tooltipRoot.innerHTML = innerHtml;
						}

						// `this` will be the overall tooltip
						var position = this._chart.canvas.getBoundingClientRect();

						// Display, position, and set styles for font
						tooltipEl.style.opacity = 1;
						if (settings.options.tooltips.lineMode) {
							tooltipEl.style.left = tooltipModel.caretX + 'px';
						} else {
							tooltipEl.style.left = position.left + window.pageXOffset + tooltipModel.caretX - (tooltipEl.offsetWidth / 2) - 3 + 'px';
						}
						tooltipEl.style.top = position.top + window.pageYOffset + tooltipModel.caretY - tooltipEl.offsetHeight - 25 + 'px';
						tooltipEl.style.pointerEvents = 'none';
						tooltipEl.style.transition = settings.options.tooltips.transition;
					}
				}
			}
		}, dataSettings, this.settings);

		/* Start : Init */

		var newChartJS = new Chart(el, this.settings);

		/* End : Init */

		return newChartJS;
	}
}
