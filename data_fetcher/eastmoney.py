"""EastMoney data fetcher for A-share market data."""
import requests
from typing import Optional, Dict, Any, List


class EastMoneyFetcher:
    """Fetch A-share real-time quotes and market data from EastMoney/Tencent QQ API."""

    def get_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for A-share stock.

        Args:
            symbol: A-share stock code (e.g., "600519" for Moutai, "000001" for Ping An)

        Returns:
            Dict with current_price, change, change_percent, volume, etc.
        """
        try:
            # Determine market prefix (sh=上海, sz=深圳)
            if symbol.startswith("6"):
                prefix = "sh"
            else:
                prefix = "sz"

            url = f"https://qt.gtimg.cn/q={prefix}{symbol}"
            resp = requests.get(url, timeout=10)

            if resp.status_code != 200:
                return None

            # Parse Tencent QQ API response format
            # v_sh600519="1~贵州茅台~600519~1467.50~1446.90~..."
            content = resp.text.strip()
            if "=\"\"\" " in content or content.count("~") < 10:
                return None

            # Extract data between quotes
            data_str = content.split("=\"")[1].split("\"")[0] if "\"" in content else ""
            if not data_str:
                return None

            fields = data_str.split("~")
            if len(fields) < 10:
                return None

            current_price = float(fields[3]) if fields[3] else 0
            prev_close = float(fields[4]) if fields[4] else 0
            open_price = float(fields[5]) if fields[5] else 0
            volume = int(fields[6]) if fields[6] else 0  # Volume in lots (hand)
            amount = float(fields[37]) if len(fields) > 37 and fields[37] else 0  # Amount in yuan
            high = float(fields[33]) if len(fields) > 33 and fields[33] else 0
            low = float(fields[34]) if len(fields) > 34 and fields[34] else 0
            name = fields[1] if len(fields) > 1 else symbol

            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0

            return {
                "symbol": symbol,
                "name": name,
                "current_price": current_price,
                "prev_close": prev_close,
                "open": open_price,
                "volume": volume * 100,  # Convert lots to shares
                "amount": amount,
                "high": high,
                "low": low,
                "change": change,
                "change_percent": change_percent,
            }
        except Exception as e:
            print(f"Error fetching A-share quote for {symbol}: {e}")
            return None

    def get_market_indices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get major A-share market indices.

        Returns:
            Dict mapping index name to index data.
        """
        indices_map = {
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            "sh000300": "沪深300",
        }
        result = {}
        try:
            for secid, name in indices_map.items():
                prefix = secid[:2]
                code = secid[2:]
                url = f"https://qt.gtimg.cn/q={prefix}{code}"
                resp = requests.get(url, timeout=10)

                if resp.status_code != 200:
                    continue

                content = resp.text.strip()
                data_str = content.split("=\"")[1].split("\"")[0] if "\"" in content else ""
                if not data_str:
                    continue

                fields = data_str.split("~")
                if len(fields) < 10:
                    continue

                current_price = float(fields[3]) if fields[3] else 0
                prev_close = float(fields[4]) if fields[4] else 0
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close else 0

                result[name] = {
                    "symbol": secid,
                    "current_price": current_price,
                    "change": change,
                    "change_percent": change_percent,
                }
        except Exception as e:
            print(f"Error fetching market indices: {e}")
        return result

    def get_sector_fund_flow(self) -> List[Dict[str, Any]]:
        """
        Get sector fund flow data (主力净流入排行).

        Returns:
            List of sector flow data.
        """
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 20,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f62",
                "fs": "m:90+t:2",
                "fields": "f12,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124",
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            result = []
            if data.get("data") and data["data"].get("diff"):
                for item in data["data"]["diff"]:
                    result.append({
                        "symbol": item.get("f12"),
                        "name": item.get("f14"),
                        "net_inflow": item.get("f62", 0),
                        "net_inflow_percent": item.get("f184", 0),
                    })
            return result
        except Exception as e:
            print(f"Error fetching sector fund flow: {e}")
            return []
