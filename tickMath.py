import jsbi
import decimal
MAX_TICK = jsbi.BigInt('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')




def tickToPrice(tick: int,token0Decimal: int = 18, token1Decimal: int = 18) -> decimal:
    sqrtPriceX96 = getSqrtRatioAtTick(tick)
    decimalSub = token0Decimal - token1Decimal
    return 1.0001 ** tick


# tick to sqrtPriceX96
def getSqrtRatioAtTick(tick: int) -> int:
    absTick = abs(tick)
    assert absTick <= MAX_TICK, 'T'

    ratio = 0xfffcb933bd6fad37aa2d162d1a594001 if absTick & 0x1 != 0 else 0x100000000000000000000000000000000
    if absTick & 0x2 != 0:
        ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128
    if absTick & 0x4 != 0:
        ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128
    if absTick & 0x8 != 0:
        ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0) >> 128
    if absTick & 0x10 != 0:
        ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644) >> 128
    if absTick & 0x20 != 0:
        ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0) >> 128
    if absTick & 0x40 != 0:
        ratio = (ratio * 0xff2ea16466c96a3843ec78b326b52861) >> 128
    if absTick & 0x80 != 0:
        ratio = (ratio * 0xfe5dee046a99a2a811c461f1969c3053) >> 128
    if absTick & 0x100 != 0:
        ratio = (ratio * 0xfcbe86c7900a88aedcffc83b479aa3a4) >> 128
    if absTick & 0x200 != 0:
        ratio = (ratio * 0xf987a7253ac413176f2b074cf7815e54) >> 128
    if absTick & 0x400 != 0:
        ratio = (ratio * 0xf3392b0822b70005940c7a398e4b70f3) >> 128
    if absTick & 0x800 != 0:
        ratio = (ratio * 0xe7159475a2c29b7443b29c7fa6e889d9) >> 128
    if absTick & 0x1000 != 0:
        ratio = (ratio * 0xd097f3bdfd2022b8845ad8f792aa5825) >> 128
    if absTick & 0x2000 != 0:
        ratio = (ratio * 0xa9f746462d870fdf8a65dc1f90e061e5) >> 128
    if absTick & 0x4000 != 0:
        ratio = (ratio * 0x70d869a156d2a1b890bb3df62baf32f7) >> 128
    if absTick & 0x8000 != 0:
        ratio = (ratio * 0x31be135f97d08fd981231505542fcfa6) >> 128
    if absTick & 0x10000 != 0:
        ratio = (ratio * 0x9aa508b5b7a84e1c677de54f3e99bc9) >> 128
    if absTick & 0x20000 != 0:
        ratio = (ratio * 0x5d6af8dedb81196699c329225ee604) >> 128
    if absTick & 0x40000 != 0:
        ratio = (ratio * 0x2216e584f5fa1ea926041bedfe98) >> 128
    if absTick & 0x80000 != 0:
        ratio = (ratio * 0x48a170391f7dc42444e8fa2) >> 128

    if tick > 0:
        ratio = MAX_TICK

    sqrtPriceX96 = (ratio >> 32) + (0 if ratio % (1 << 32) == 0 else 1)
    return sqrtPriceX96