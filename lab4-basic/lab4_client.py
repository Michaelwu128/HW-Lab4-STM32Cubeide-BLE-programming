import asyncio
import struct
import sys
from bleak import BleakClient

DEVICE_ADDRESS = "C2:D4:FE:69:B3:EB"
ACC_CHAR_UUID = "201f1e1d-1c1b-1a19-1817-161514131211"
FREQ_CHAR_UUID = "302f2e2d-2c2b-2a29-2827-262524232221"

def notification_handler(sender, data):
    x, y, z = struct.unpack('<hhh', data[:6])
    # 使用 \r 讓數據在同一行跳動，才不會洗掉你的輸入框
    sys.stdout.write(f"\r📍 [即時數據] X: {x:6d} | Y: {y:6d} | Z: {z:6d}  ")
    sys.stdout.flush()

async def interactive_write(client):
    """這是一個專門等待你輸入頻率的任務"""
    while True:
        try:
            # 在非同步環境下獲取使用者輸入
            val_str = await asyncio.to_thread(input, "\n👉 請輸入新的採樣頻率 (ms) [或按 Ctrl+C 結束]: ")
            if val_str.isdigit():
                new_delay = int(val_str)
                # 寫入板子
                await client.write_gatt_char(FREQ_CHAR_UUID, struct.pack('<H', new_delay))
                print(f"✅ 已發送指令！頻率改為: {new_delay} ms")
            else:
                print("⚠️ 請輸入有效的數字。")
        except Exception as e:
            print(f"💥 寫入失敗: {e}")
            break

async def run_lab4():
    print(f"--- 正在連線至: {DEVICE_ADDRESS} ---")
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("✨ 連線成功！現在你可以一邊看數據，一邊手動輸入頻率。")

        # 1. 啟動通知 (在背景跑)
        await client.start_notify(ACC_CHAR_UUID, notification_handler)

        # 2. 啟動互動輸入任務
        await interactive_write(client)

if __name__ == "__main__":
    try:
        asyncio.run(run_lab4())
    except KeyboardInterrupt:
        print("\n👋 程式已由使用者結束。")