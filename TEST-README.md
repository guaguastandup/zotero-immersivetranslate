
# 测试弹窗1:
网络连接正常, 通过健康检查，但是下载超时。

```python
# run test_download_server.py
# test on "http://localhost:8765";
python test_download_server.py
```

# 测试弹窗2

网络连接错误, 未通过健康检查，下载超时。

step1: 
```python
# run test_download_server.py
# test on "http://localhost:8765";
python test_download_server.py
```

step2:
修改utils/const.ts中的健康检查链接
