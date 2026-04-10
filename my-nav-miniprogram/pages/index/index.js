Page({
  data: {
    links: [],
    categories: [],
    filteredLinks: [],
    searchText: ''
  },

  onLoad() {
    this.loadLinks();
    this.loadCategories();
  },

  // 加载链接
  async loadLinks() {
    try {
      const res = await wx.request({
        url: `${getApp().globalData.apiUrl}/links`,
        method: 'GET'
      });

      if (res.data.success) {
        this.setData({
          links: res.data.data,
          filteredLinks: res.data.data
        });
      }
    } catch (error) {
      console.error('加载链接失败:', error);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    }
  },

  // 加载分类
  async loadCategories() {
    try {
      const res = await wx.request({
        url: `${getApp().globalData.apiUrl}/categories`,
        method: 'GET'
      });

      if (res.data.success) {
        this.setData({
          categories: res.data.data
        });
      }
    } catch (error) {
      console.error('加载分类失败:', error);
    }
  },

  // 搜索
  onSearch(e) {
    const searchText = e.detail.value.toLowerCase();
    const filteredLinks = this.data.links.filter(link =>
      link.title.toLowerCase().includes(searchText) ||
      (link.description && link.description.toLowerCase().includes(searchText))
    );

    this.setData({
      searchText,
      filteredLinks
    });
  },

  // 点击链接
  async onLinkTap(e) {
    const link = e.currentTarget.dataset.link;

    // 记录点击
    try {
      await wx.request({
        url: `${getApp().globalData.apiUrl}/links/${link.id}/click`,
        method: 'POST'
      });
    } catch (error) {
      console.error('记录点击失败:', error);
    }

    // 复制链接或跳转
    wx.showModal({
      title: link.title,
      content: `是否打开链接：${link.url}`,
      success: (res) => {
        if (res.confirm) {
          wx.setClipboardData({
            data: link.url,
            success: () => {
              wx.showToast({
                title: '链接已复制',
                icon: 'success'
              });
            }
          });
        }
      }
    });
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadLinks();
    this.loadCategories();
    wx.stopPullDownRefresh();
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '我的导航站',
      path: '/pages/index/index'
    };
  }
});
