using Test
using MacroAIComp

@testset "Growth Tests" begin
    @testset "Solow Steady State Calibration" begin
        params = default_calibration(SolowSwanParameters)
        ss = compute_solow_steady_state(params)

        @test ss["k"] ≈ 4.0946 atol=1e-4
        @test ss["y"] ≈ 1.6378 atol=1e-4
        @test ss["c"] ≈ 1.3103 atol=1e-4
        @test ss["i"] ≈ 0.3276 atol=1e-4
    end

    @testset "Savings Shock Dynamics" begin
        params = default_calibration(SolowSwanParameters)
        ss_init = compute_solow_steady_state(params)

        T = 150
        s_path = fill(0.25, T)
        n_path = fill(params.n, T)
        A_path = fill(1.00, T)

        res = simulate_solow_swan(params, ss_init["k"], s_path, n_path, A_path, T)

        # 1. Capital should start at initial steady state and grow monotonically
        @test res["k"][1] ≈ ss_init["k"]
        for t in 1:(T - 1)
            @test res["k"][t + 1] > res["k"][t]
        end

        # 2. Output should start at initial steady state and grow monotonically
        @test res["y"][1] ≈ ss_init["y"]
        for t in 1:(T - 1)
            @test res["y"][t + 1] > res["y"][t]
        end

        # 3. Consumption must jump down immediately on impact due to higher savings rate
        @test res["c"][1] < ss_init["c"]
        @test res["c"][1] ≈ 0.75 * ss_init["y"]

        # 4. Eventually, capital accumulation leads to higher output and consumption
        ss_final = compute_solow_steady_state(params, 0.25)
        @test res["k"][end] ≈ ss_final["k"] atol=1e-2
        @test res["y"][end] ≈ ss_final["y"] atol=1e-2
        @test res["c"][end] ≈ ss_final["c"] atol=1e-2
        @test res["c"][end] > ss_init["c"]

        # 5. Output growth rate gy should jump up and then converge back to 0
        @test res["gy"][1] == 0.0
        @test res["gy"][2] > 0.0
        for t in 3:(T - 1)
            @test res["gy"][t] > 0.0
            @test res["gy"][t] < res["gy"][t - 1]
        end
        @test res["gy"][end] ≈ 0.0 atol=1e-2
    end

    @testset "Golden Rule Calculation" begin
        params = default_calibration(SolowSwanParameters)
        alpha = params.alpha

        # Golden rule steady state (s = alpha)
        ss_gold = compute_solow_steady_state(params, alpha)
        c_gold = ss_gold["c"]

        # Under-accumulated capital steady state (s < alpha)
        ss_low = compute_solow_steady_state(params, 0.20)
        @test ss_low["c"] < c_gold

        # Over-accumulated capital steady state (s > alpha)
        ss_high = compute_solow_steady_state(params, 0.50)
        @test ss_high["c"] < c_gold

        # Check local neighborhood around alpha
        ss_left = compute_solow_steady_state(params, alpha - 0.01)
        ss_right = compute_solow_steady_state(params, alpha + 0.01)

        @test c_gold > ss_left["c"]
        @test c_gold > ss_right["c"]
    end
end
