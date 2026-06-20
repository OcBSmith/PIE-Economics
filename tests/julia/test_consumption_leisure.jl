using Test
using MacroAIComp

@testset "ConsumptionLeisure Tests" begin
    @testset "Equivalence fsolve and optim" begin
        params = default_calibration(ConsumptionLeisureParameters)
        W = fill(30.0, params.T)

        res_fsolve = solve_foc_fsolve(params, W)
        res_optim = solve_direct_optim(params, W)

        @test res_fsolve["C"] ≈ res_optim["C"] atol=1e-3
        @test res_fsolve["L"] ≈ res_optim["L"] atol=1e-3
        @test res_fsolve["B"] ≈ res_optim["B"] atol=1e-3
    end

    @testset "Terminal Condition" begin
        params = default_calibration(ConsumptionLeisureParameters)
        W = fill(30.0, params.T)

        res_fsolve = solve_foc_fsolve(params, W)
        res_optim = solve_direct_optim(params, W)

        @test abs(res_fsolve["B"][end]) < 1e-6
        @test abs(res_optim["B"][end]) < 1e-6
    end

    @testset "Leisure Consumption Tradeoff" begin
        params = default_calibration(ConsumptionLeisureParameters)
        W = fill(30.0, params.T)

        res = solve_foc_fsolve(params, W)

        @test all(l -> l >= 0.0, res["L"])
        @test all(l -> l < 1.0, res["L"])
        @test all(o -> o > 0.0, res["O"])
        @test all(o -> o <= 1.0, res["O"])
    end

    @testset "Preference Sensitivity" begin
        params_low = ConsumptionLeisureParameters(30, 0.97, 0.02, 0.40, 0.0)
        params_high = ConsumptionLeisureParameters(30, 0.97, 0.02, 0.60, 0.0)
        W = fill(30.0, params_low.T)

        res_low = solve_foc_fsolve(params_low, W)
        res_high = solve_foc_fsolve(params_high, W)

        mean_l_high = sum(res_high["L"]) / length(res_high["L"])
        mean_l_low = sum(res_low["L"]) / length(res_low["L"])

        @test mean_l_high > mean_l_low
    end

    @testset "Interest Rate Slope" begin
        params = ConsumptionLeisureParameters(30, 0.97, 0.05, 0.5, 0.0)
        W = fill(30.0, params.T)

        res = solve_foc_fsolve(params, W)

        for t in 1:(params.T - 1)
            @test res["C"][t + 1] > res["C"][t]
        end
    end
end
