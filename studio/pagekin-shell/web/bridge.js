/**
 * 浏览器侧的 aiNovelAPI 实现。
 *
 * Electron 环境里 preload 已经注入了 window.aiNovelAPI，本文件检测到后立即退出，
 * 因此同一份前端产物在桌面与 Web 两种形态下都能用。
 */
(function () {
  if (window.aiNovelAPI) return;

  var listeners = new Map();
  var source = null;

  function ensureEvents() {
    if (source) return source;
    source = new EventSource("/events");
    source.onmessage = function (ev) {
      try {
        var payload = JSON.parse(ev.data);
        var set = listeners.get(payload.channel);
        if (!set) return;
        set.forEach(function (fn) {
          try {
            fn.apply(null, payload.args || []);
          } catch (e) {
            console.error("[bridge] listener error", payload.channel, e);
          }
        });
      } catch (e) {
        console.error("[bridge] bad event", e);
      }
    };
    source.onerror = function () {
      try {
        source.close();
      } catch (e) {}
      source = null;
      setTimeout(ensureEvents, 1500);
    };
    return source;
  }

  function rpc(channel, args) {
    return fetch("/rpc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel: channel, args: args }),
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data.ok) {
          var err = new Error(data.error || "RPC 调用失败");
          err.channel = channel;
          throw err;
        }
        return data.result;
      });
  }

  window.aiNovelAPI = {
    invoke: function (channel) {
      var args = Array.prototype.slice.call(arguments, 1);
      return rpc(channel, args);
    },
    on: function (channel, callback) {
      ensureEvents();
      if (!listeners.has(channel)) listeners.set(channel, new Set());
      listeners.get(channel).add(callback);
      return function () {
        var set = listeners.get(channel);
        if (set) set.delete(callback);
      };
    },
    once: function (channel, callback) {
      var off = window.aiNovelAPI.on(channel, function () {
        off();
        callback.apply(null, arguments);
      });
    },
    send: function (channel) {
      var args = Array.prototype.slice.call(arguments, 1);
      rpc(channel, args).catch(function () {});
    },
    setZoomLevel: function () {},
    setZoomFactor: function () {},
    getZoomLevel: function () {
      return 0;
    },
  };
})();
