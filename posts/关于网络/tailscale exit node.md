# 使用 Tailscale 把树莓派设置成 VPN 出口（Exit Node）

这是一份简短版步骤，适合已经装好 Tailscale 的情况。

## 1. 在树莓派上开启 IP 转发

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

可选检查：

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

## 2. 把树莓派声明为 Exit Node

```bash
sudo tailscale set --advertise-exit-node
```

查看状态：

```bash
tailscale status
```

## 3. 在 Tailscale 后台批准这台设备

进入 Tailscale 管理后台，找到你的树莓派设备，例如 `willman`，确认它可以作为 **Exit Node** 使用。

![这是图片](https://img.lxxsfile.org/assets/056de04bc0fcfe9d1dbdfa840ff4e519249fc256301b1741458bc5212dc5160f.png)

## 4. 在另一台设备上使用这个 Exit Node

在 Windows / 手机 / 其他电脑上打开 Tailscale，找到 **Exit nodes**，选择你的树莓派。

如果需要，也可以勾选：

- **Allow local network access**

这样在使用出口节点时，仍然可以访问当前局域网里的设备。

## 5. 测试是否成功

最简单的方法：

1. 先关闭 Exit Node，查询一次公网 IP  
2. 再开启 Exit Node，再查一次公网 IP

如果第二次显示的是**树莓派所在网络的公网 IP**，说明成功。

例如在 Windows PowerShell 中可用：

```powershell
curl ifconfig.me
```

## 6. 一句话总结

Tailscale 作为 VPN 出口的原理就是：

**客户端先通过 Tailscale 加密连接到树莓派，再由树莓派代替客户端访问外网。**

这样外部网站看到的就是树莓派所在网络的公网 IP。
